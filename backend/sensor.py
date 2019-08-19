import asyncio
import os.path
import logging
from datetime import datetime

import aiofiles
from aiohttp import web 
from aioinflux import InfluxDBClient

from .service import Service

logger = logging.getLogger(__name__)


class AnalogSensor(Service):
    def __init__(self, sensor, name, period=60):
        super().__init__(name)
        self.sensor = sensor
        self.period = period
        self.config = {
            "name": self.name,
            "type": "AnalogSensor",
            "unit": "C",
            "sensor": self.sensor.id(),
            "period": self.period
        }
        self.add_route(
            web.get('/api/{}/card'.format(self.name), self.card_request)
        )

    async def card_request(self, request):
        influx = request.app["influx-db"]

        last = await self.get_last_sample(influx)
        if last is None:
            return web.json_response({
                "name": self.name,
                "error": "No Data Available"
            })

        time, value = last
        return web.json_response({
            "name": self.name,
            "value": value,
            "time": time
        })

    async def event_handler(self, app):
        """
        The handler loop for a temperature sensor.

        Every (N) seconds, the sensor is queried.
        """
        loop = asyncio.get_running_loop()
        influx = app["influx-db"]

        self.log.info("Starting event handler.")
        while not self.shutdown_event.is_set():
            tick = loop.time()

            temp = await self.sensor.read_value()
            await self.record_sample(influx, temp)
            self.log.debug("Aquired sample: %f", temp)

            elapsed = loop.time() - tick

            next_call = self.period - elapsed
            if next_call < 0:
                next_call = 0

            await asyncio.sleep(next_call)

        self.log.info("Stopped event handler.")
