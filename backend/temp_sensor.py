import asyncio
import os.path
from datetime import datetime

import aiofiles
from aiohttp import web 
from aioinflux import InfluxDBClient


class TempSensor():
    def __init__(self, **config):
        """
        Config Object:
        {
            "path": "/sys/class/hwmon/hwmon0/temp1_input",
            "name": "my sensor",
            "period": 60, # seconds
        }
        """
        self.path = config.get("path", None)
        if not os.path.exists(self.path):
            raise ValueError("Could not find temperature sensor in '{}'".format(self.path))
        
        self.name = config.get("name", "temperature")
        self.period = config.get("period", 60)

    def return_config(self):
        """ Returns the configuration of the sensor """
        return web.json_response({
            "path": self.path,
            "name": self.name,
            "update_period": self.period
        })

    async def read_temperature(self):
        async with aiofiles.open(self.path, 'r') as sensor:
            temp = await sensor.readline()
        return int(temp) / 1000.0

    async def record_temperature(self, db, temperature):
        """ Add the temperature to the database """
        print("Temp:", self.name, temperature)
        return await db.write({
            "measurement": "samples",
            "time": datetime.now(),
            "tags": {"name": self.name},
            "fields": {"value": temperature}
        })

    async def get_request(self, request):
        """ Returns the configuration of the sensor """
        return self.return_config()

    async def put_request(self, request):
        #TODO: Update from request
        return self.return_config()

    async def value_request(self, request):
        """Returns the values from the database for this sensor

        URL Parameters:
            - "begin": 
            - "end": 
            - "every" (duration): return min/max values sampled every 'duration' 
        
        
        """
        influx = request.app["influx-db"]
        resp = await influx.query("""SELECT value FROM "samples" WHERE "name"='{name}'""".format(name=self.name))
        return web.json_response(resp)

    async def event_handler(self, app):
        """
        The handler loop for a temperature sensor.

        Every (N) seconds, the sensor is queried.
        """
        loop = asyncio.get_running_loop()
        influx = app["influx-db"]

        while True:
            tick = loop.time()

            temp = await self.read_temperature()
            await self.record_temperature(influx, temp)

            elapsed = loop.time() - tick

            next_call = self.period - elapsed
            if next_call < 0:
                next_call = 0

            await asyncio.sleep(next_call)

    def routes(self):
        return [
            web.get('/api/temp', self.get_request),
            web.put('/api/temp', self.put_request),
            web.get('/api/temp/value', self.value_request)
        ]


