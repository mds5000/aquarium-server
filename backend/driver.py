from flask import Flask
from flask_jsonrpc import JSONRPC
from gevent.pywsgi import WSGIServer
import gevent

from schema import db, Device

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
rpc = JSONRPC(app, '/rpc')
db.init_app(app)

class Driver():
    app = app
    rpc = rpc
    db = db

    @classmethod
    def register_device(cls, driver_key, name, description, units=None):
        dev = Driver.lookup_device(driver_key, name)
        if not dev:
            dev = Device(provider=driver_key,
                        provider_name=name,
                        description=description,
                        units=units)
            db.session.add(dev)
            db.session.commit()
            dev = Driver.lookup_device(driver_key, name)
        return dev

    @classmethod
    def lookup_device(cls, driver_key, name):
        return Device.query.filter_by(provider=driver_key)\
                           .filter_by(provider_name=name)\
                           .first()

    @classmethod
    def spawn(cls, function, when=0):
        gevent.spawn_later(when, function)

    @classmethod
    def periodic(cls, function):
        def _task():
            while True:
                next_period = function()
                if next_period:
                    gevent.sleep(next_period)
                else:
                    break
        gevent.spawn(_task)

    @classmethod
    def serve(cls, host, port):
        server = WSGIServer((host, port), cls.app)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass



