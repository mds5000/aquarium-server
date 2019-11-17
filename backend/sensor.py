import asyncio
import os.path
import logging
import json
from datetime import datetime

import aiofiles
from aiohttp import web 
from aioinflux import InfluxDBClient

from .service import Service

logger = logging.getLogger(__name__)


class AnalogSensor(Service):
    def __init__(self, sensor, name, period=60, unit="C", scaling=[1, 0]):
        super().__init__(name)
        self.sensor = sensor
        self.period = period
        self.scaling = scaling
        self.unit = unit
        self.config = {
            "name": self.name,
            "type": "AnalogSensor",
            "sensor": self.sensor.id(),
            "period": self.period
        }
        self.add_route(
            web.get('/api/{}/card'.format(self.name), self.card_request)
        )

    async def card_request(self, request):
        influx = request.app["influx-db"]

        last_data = await self.get_last(influx, self.name)
        if last_data is None:
            return web.HTTPServiceUnavailable(reason="No data available.")

        time, value = last_data
        return web.json_response({
            "name": self.name,
            "value": value,
            "time": time,
            "unit": self.unit
        })

    async def event_handler(self, app):
        """
        The handler loop for a temperature sensor.

        Every (N) seconds, the sensor is queried.
        """
        loop = asyncio.get_running_loop()
        influx = app["influx-db"]

        #self.calibration = self.load_calibration(influx)

        self.log.info("Starting event handler.")
        while not self.shutdown_event.is_set():
            tick = loop.time()

            value = await self.sensor.read_value()
            scaled_value = self.scaling[0] * value + self.scaling[1]
            await self.record_sample(influx, self.name, scaled_value)
            self.log.debug("Aquired sample: %f -> %f", value, scaled_value)

            elapsed = loop.time() - tick

            next_call = self.period - elapsed
            if next_call < 0:
                next_call = 0

            await asyncio.sleep(next_call)

        self.log.info("Stopped event handler.")


class CalibratableSensor(AnalogSensor):
    def __init__(self, sensor, name, period=60, unit="C", scaling=[1, 0]):
        super().__init__(sensor, name, period, unit, scaling)
        self.add_route(
            web.get('/api/{}/calibration'.format(self.name), self.get_calibration_request),
            web.post('/api/{}/calibration'.format(self.name), self.post_calibration_request)
        )

    async def get_calibration_request(self, request):
        influx = request.app["influx-db"]
        _, calibration = await self.get_last(influx, "calibration")
        slope, offset = json.loads(calibration)

        if calibration is None:
            return web.HTTPServiceUnavailable(reason="No calibration data avialable.")
        return web.json_response({"slope": slope, "offset": offset})

    async def post_calibration_request(self, request):
        influx = request.app["influx-db"]

        new_calibration = await request.json()
        slope = new_calibration.get("slope")
        offset = new_calibration.get("offset")
        if slope is None or offset is None:
            return web.HTTPBadRequest(reason="Calibration must include a slope and offset.")
        
        slope, offset = float(slope), float(offset)
        self.scaling = (slope, offset)
        await self.record_event(influx, "calibration", json.dumps(self.scaling))
        self.log.info("Updated calibration: slope=%f, offset=%f", slope, offset)
        return web.json_response({"slope": slope, "offset": offset})


