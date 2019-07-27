import asyncio
import os

from aiohttp import web 
from aioinflux import InfluxDBClient

from .device import HwmonDevice, GpioPin, PwmPin
from .sensor import AnalogSensor
from .dosing_pump import DosingPump
from .kessil import KessilController


async def initialize_database(app):
    db_host = os.getenv("INFLUXDB_HOST", "localhost")
    db_port = os.getenv("INFLUXDB_PORT", 8086)
    db_database = os.getenv("ENVIRONMENT", "aquarium")
    db = InfluxDBClient(host=db_host, port=db_port, db=db_database)
    app["influx-db"] = db
    await db.create_database(db=db_database)

async def initialize_application(app):
    loop = asyncio.get_event_loop()
    for driver in app['services']:
        loop.create_task(driver.event_handler(app))
        app.add_routes(driver.routes())

async def shutdown_application(app):
    drivers = app.get('services', [])
    done, pending = await asyncio.wait(drivers, timeout=5.0)
    for task in pending:
        print("Failed to stop Task", task)

def main():
    app = web.Application()
    pin17 = GpioPin(17)
    pwm0 = PwmPin(0)
    pwm1 = PwmPin(1)
    temp_sensor = HwmonDevice("temp1_input")

    app['services'] = [
        AnalogSensor(temp_sensor, "temperature"),
        DosingPump(pin17, "pump"),
        KessilController(pwm0, pwm1, "kessil")
    ]

    app.on_startup.append(initialize_application)
    app.on_startup.append(initialize_database)
    #app.on_shutdown.append(shutdown_application)

    web.run_app(app)

if __name__ == '__main__':
    main()