"""
To run:
    $ export FLASK_APP=server.py
    $ export FLASK_ENV=development
    $ flask run (or python -m flask run)
"""
from flask import Flask, jsonify, send_from_directory, request
from flask_mqtt import Mqtt
from schema import db, Device, Measurement, Event

import json

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

app.config['MQTT_CLIENT_ID'] = 'server'
app.config['MQTT_BROKER_URL'] = 'msunderland-lin'
app.config['MQTT_BROKER_PORT'] = 1883
mqtt = Mqtt()
mqtt.init_app(app)

@app.route('/static/<path:path>')
def static_server(path):
    return send_from_directory('../app', path)

@app.route('/api/devices')
def devices_api():
    return jsonify([d.serialize() for d in Device.query.all()])

@app.route('/api/device', methods=['GET'])
def device_api():
    """ URL Parameters:
    id=0
    name='name'
    address='provider/device'
    """
    filter = {}
    if 'id' in request.args:
        filter = {"id": request.args['id']}
    elif 'address' in request.args:
        filter = {"address": request.args['address']}
    elif 'name' in request.args:
        filter = {"name": request.args['name']}
    else:
        return "Must provide one of 'id', 'name', or 'address' as query parameter.", 400

    try:
        device = Device.query.filter_by(**filter).one()
        return jsonify(device.serialize())
    except NoResultFound:
        return "No device found matching query.", 404
    except MultipleResultsFound:
        return "Multiple devices found matching query.", 404

@app.route('/api/device/<int:id>', methods=['POST', 'DELETE'])
def device_modify_api(id):
    if request.method == "DELETE":
        Device.query.filter_by(id=id).delete()
        db.session.commit()
        return str(id), 200
    
    else:
        updated_device = request.get_json()
        updated_device.pop('address', None)  # Can't modify device's address
        updated_device.pop('id', None)       # or it's ID
        Device.query.filter_by(id=id).update(updated_device)
        db.session.commit()
        return jsonify(Device.query.get(id).serialize())

@app.route('/api/measurements')
def measurements_api():
    """ URL Parameters:
    from: (DateTime) Return data collected after this date.
    to: (DateTime) Return data collected up to this date.
    id: (int[,...]) Return data for devices with 'id', multiple allowed
    include_comments: Return measurement comments with the data.

    Response:
        [
            {"id": 0, "timestamp": t0, "value": value, "comment": comment},
            {"id": 1, "timestamp": t1, "value": value, "comment": null},
            ...
        ]
    """
    columns = [Measurement.id, Measurement.timestamp, Measurement.value]
    if 'include_comments' in request.args:
        columns.append(Measurement.comment)

    query = db.session.query(*columns).order_by(Measurement.timestamp)

    if 'id' in request.args:
        query = query.filter(Measurement.id.in_(request.args["id"]))

    if 'from' in request.args:
        query = query.filter(Measurement.timestamp > request.args["from"])

    if 'to' in request.args:
        query = query.filter(Measurement.timestamp < request.args["from"])

    return jsonify(query.all())

@app.route("/api/measurement", methods=["POST"])
def measurement_api():
    payload = request.get_json()

    measurement = Measurement(
        device=payload["id"],
        value=payload["value"],
        comment=payload.get("comment")
    )
    db.session.add(measurement)
    db.session.commit()

    return jsonify(measurement.serialize())


@app.route('/api/events')
def events_api():
    """ URL Parameters:
    from: (DateTime) Return data collected after this date.
    to: (DateTime) Return data collected up to this date.
    id: (int[,...]) Return data for devices with 'id', multiple allowed
    Response:
        [
            {"id": 0, "timestamp": t0, "value": value, "comment": comment},
            {"id": 1, "timestamp": t1, "value": value, "comment": null},
            ...
        ]
    """
    columns = [Event.id, Event.timestamp, Event.value, Event.comment]
    query = db.session.query(*columns).order_by(Event.timestamp)

    if 'id' in request.args:
        query = query.filter(Event.id.in_(request.args["id"]))

    if 'from' in request.args:
        query = query.filter(Event.timestamp > request.args["from"])

    if 'to' in request.args:
        query = query.filter(Event.timestamp < request.args["from"])

    return jsonify(query.all())


@mqtt.on_connect()
def handle_mqtt_connection(client, userdata, flags, ret_code):
    app.logger.info("Connected to MQTT Broker: %s", client)

    with app.app_context():
        app.logger.info("Loading existing devices from database:")
        for device in Device.query.all():
            add_new_device(device.address)

    mqtt.subscribe("new_device")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    topic = message.topic
    payload = json.loads(message.payload)
    app.logger.debug("MQTT Message: %s, %s", topic, message.payload)

    with app.app_context():

        if topic == "new_device":
            device = Device.query.filtery_by(address=payload["name"]).one_or_none()
            if device is None:
                device = Device(
                    address=payload["name"],
                    description=payload.get("description", ""),
                    units=payload.get("units")
                )
                db.session.add(device)
                db.session.commit()
            add_new_device(device.address)

        elif topic.endswith("/value"):
            address = topic.rsplit("/", 1)[0]
            device = Device.query.filter_by(address=address).one()
            measurement = Measurement(
                device=device.id,
                value=payload["value"],
                comment=payload.get("comment")
            )
            db.session.add(measurement)
            db.session.commit()

        elif topic.endswith("/update"):
            address = topic.rsplit("/", 1)[0]
            device = Device.query.filter_by(address=address).one()
            event = Event(
                device=device.id,
                action=payload["action"],
                value=payload["value"],
                comment=payload.get("comment")
            )
            db.session.add(event)
            db.session.commit()

        else:
            app.logger.warn("Unhandled MQTT Message '%s'", topic)


def add_new_device(address):
    app.logger.info("Register Device '%s'", address)
    mqtt.subscribe("{}/value".format(address))
    mqtt.subscribe("{}/update".format(address))


