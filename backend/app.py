import asyncio
import os
import logging

from aiohttp import web 
from aioinflux import InfluxDBClient

from .device import HwmonDevice, GpioPin, PwmPin
from .sensor import AnalogSensor
from .dosing_pump import DosingPump
from .switch import Switch
from .kessil import KessilController

logger = logging.getLogger(__name__)


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

async def list_services(request):
    services = request.app["services"]
    return web.json_response(
        {"services": [service.config for service in services]}
    )

def main():
    logging.basicConfig(format='%(name)s-%(levelname)s: %(message)s', level=logging.DEBUG)
    logger.info("Starting aquarium server.")

    app = web.Application()
    switch_1 = GpioPin(26)
    switch_2 = GpioPin(20)
    switch_3 = GpioPin(19)
    switch_4 = GpioPin(23)
    switch_5 = GpioPin(27)
    switch_6 = GpioPin(17)

    led_0 = GpioPin(16)
    led_1 = GpioPin(24)

    pwm0 = PwmPin(0)
    pwm1 = PwmPin(1)

    temp_sensor = HwmonDevice("temp1_input")
    #ph_sensor = HwmonDevice()
    #system_temp_sensor
    #humidity_sensor

    app['services'] = [
        AnalogSensor(temp_sensor, "temperature"),
        DosingPump(switch_1, "kalk"),
        DosingPump(switch_2, "calcium"),
        Switch(led_0, "led"),
        KessilController(pwm0, pwm1, "kessil")
    ]

    app.router.add_get("/api/services", list_services)
    app.on_startup.append(initialize_application)
    app.on_startup.append(initialize_database)
    #app.on_shutdown.append(shutdown_application)

    port = 3001
    logger.info("Starting Server...")
    web.run_app(app, port=port, access_log=logger)

if __name__ == '__main__':
    main()
