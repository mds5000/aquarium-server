"""
To run:
    $ export FLASK_APP=server.py
    $ export FLASK_ENV=development
    $ flask run (or python -m flask run)
"""
from flask import Flask, jsonify, send_from_directory
from schema import db, Device, Measurement, Event

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

@app.route('/static/<path:path>')
def static_server(path):
    return send_from_directory('../app', path)

@app.route('/api/temperature')
def get_temp():
    return jsonify(Measurement.query.filter_by(device=2).first_or_404().serialize())

@app.route('/api/measurements')
def measurements_api():
    return jsonify([m.serialize() for m in Measurement.query.all()])

@app.route('/api/devices')
def devices_api():
    return jsonify([d.serialize() for d in Device.query.all()])

@app.route('/api/events')
def events_api():
    return jsonify([e.serialize() for e in Event.query.all()])