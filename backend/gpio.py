import asyncio
import os.path
from datetime import datetime

import aiofiles
from aiohttp import web 
from aioinflux import InfluxDBClient


class Gpio():
    def __init__(self, number, name, direction="out", root="/sys/class/gpio"):
        """
        """
        self.path = os.path.join(self.root, "gpio{}".format(number))
        if not os.path.exists(self.path):
            self._export_gpio(root, number)

        self.name = name
        self._set_direction(direction)
    
    def _export_gpio(self, root, pin):
        with open(os.path.join(root, "export"), 'w') as export:
            export.write("{}\n".format(pin))
        if not os.path.exists(self.path):
            raise RuntimeError("Could not export GPIO: '{}'".format(self.path))

    def _set_direction(self, direction):
        if direction not in ["in", "out"]:
            raise ValueError("GPIO direction must be one of 'in' or 'out', not '{}'".format(direction))

        self.direction = direction
        with open(os.path.join(self.path, "direction"), 'w') as gpio:
            gpio.write(direction)

    async def set_state(self, state):
        state = '1\n' if state else '0\n'
        async with aiofiles.open(os.path.join(self.path, "value"), 'w') as gpio:
            await gpio.write(state)

    async def get_state(self):
        async with aiofiles.open(os.path.join(self.path, "value"), 'r') as gpio:
            state = await gpio.read()
        return state[0] == '1'

    def return_config(self):
        """ Returns the configuration of the sensor """
        return web.json_response({
            "path": self.path,
            "name": self.name,
            "direction": self.direction
        })

    async def record_event(self, db, state):
        """ Add the event to the database """
        return await db.write({
            "measurement": "events",
            "time": datetime.now(),
            "tags": {"name": self.name},
            "fields": {"value": state}
        })

    async def get_request(self, request):
        """ Returns the configuration of the sensor """
        return self.return_config()

    async def value_request(self, request):
        """Returns the values from the database for this sensor

        URL Parameters:
            - "begin": 
            - "end": 
        """
        begin = request.query.get("begin")
        start_condition = "" if begin is None else "AND time >= {}".format(begin)

        end = request.query.get("end")
        end_condition = "" if end is None else "AND time < {}".format(end)

        influx = request.app["influx-db"]
        resp = await influx.query(
            """
            SELECT value FROM "events" 
            WHERE "name"='{name}' {start} {end}
            """.format(name=self.name, start=start_condition, end=end_condition)
        )
        return web.json_response(resp)

    async def set_value_request(self, request):
        """Set the state of the GPIO.

        URL Parameter:
            - "state": (bool)
        
        Returns 405 - Method Not Allowed if GPIO is set as input
        """
        if self.direction == 'in':
            raise HTTPMethodNotAllowed()

        state = request.query.get("state")
        if state is None:
            raise HTTPBadRequest()

        influx = request.app["influx-db"]
        await set_state(state)
        await record_event(influx, state)
        return web.json_response({"state": state})

    def routes(self):
        return [
            web.get('/api/temp', self.get_request),
            web.get('/api/temp/value', self.value_request),
            web.put('/api/temp/value', self.set_value_request)
        ]

    async def event_handler(self, app):
        pass


