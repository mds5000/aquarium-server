from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Device(db.Model):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    provider_name = Column(String, nullable=False)
    #provider = Column(ForeignKey('providers.id'))
    provider = Column(String, nullable=False)
    display_name = Column(String)
    description = Column(String)
    units = Column(String)

    def serialize(self):
        return {
            "id": self.id,
            "address": "{}/{}".format(self.provider, self.provider_name),
            "name": self.display_name if self.display_name else self.provider_name,
            "description": self.description,
            "units": self.units
        }


"""
class Provider(db.Model):
    __tablename__ = 'providers'

    id = Column(String, primary_key=True)
    rpc_address = Column(String)
    argv = Column(String)
    pid = Column(Integer)
    devices = relationship("Device", back_populates="provider")

    def serialize(self):
        return {
            "id": self.id,
            "rpc_address": self.rpc_address,
            "argv": self.argv,
            "pid": self.pid
        }
"""


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
    value = Column(Float)
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

