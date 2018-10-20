from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Device(db.Model):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    address = Column(String, nullable=False)
    name = Column(String)
    description = Column(String)
    units = Column(String)

    def serialize(self):
        return {
            "id": self.id,
            "address": self.address,
            "name": self.name if self.name else self.address,
            "description": self.description,
            "units": self.units
        }


class Measurement(db.Model):
    __tablename__ = 'measurements'

    id = Column(Integer, primary_key=True)
    device = Column(ForeignKey('devices.id'))
    value = Column(Float, nullable=False)
    comment = Column(String)
    timestamp = Column(DateTime, server_default=func.now())

    def serialize(self):
        return {
            "id": self.id,
            "device": self.device,
            "value": self.value,
            "comment": self.comment,
            "timestamp": self.timestamp
        }


class Event(db.Model):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    device = Column(ForeignKey('devices.id'))
    action = Column(String, nullable=False)
    value = Column(String)
    comment = Column(String)
    timestamp = Column(DateTime, server_default=func.now())

    def serialize(self):
        return {
            "id": self.id,
            "device": self.device.name,
            "action": self.action,
            "value": self.value,
            "comment": self.comment,
            "timestamp": self.timestamp
        }


def __init():
    import flask
    app = flask.Flask("app")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    db.init_app(app)
    return app

    
def create_tables():
    app = __init()
    with app.app_context():
        db.create_all()
    print "Created Tables"

def drop_tables():
    app = __init()
    with app.app_context():
        db.drop_all()
    print "Dropped Tables"

def init_test_data(app):
    devices = [
        Device(address="test/device1", description="A short description"),
        Device(address="test/device2", name="My Device", description="A longer description", units='Fish')
    ]

    with app.app_context():
        for dev in devices:
            db.session.add(dev)
        db.session.commit()
