import asyncio

from aiohttp import web 
from aioinflux import InfluxDBClient

from backend.service import Service

class Switch(Service):
    def __init__(self, pin, name):
        super().__init__(name)
        self.pin = pin
        self.config = web.json_response({
            "name": self.name,
            "device": self.pin.id()
        })
        self.add_route(
            web.get('/api/{}/state'.format(self.name), self.get_state_request),
            web.post('/api/{}/state'.format(self.name), self.set_state_request),
            web.get('/api/{}/card'.format(self.name), self.card_request)
        )

    async def set_state_request(self, request):
        """Set the state of the GPIO.

        Form Parameter:
            - "state": "true" or "false"
        
        Returns 405 - Method Not Allowed if GPIO is set as input
        """
        if self.pin.direction() == 'in':
            raise web.HTTPMethodNotAllowed()

        state = (await request.post()).get("state")
        if state is None:
            #TODO LOG
            raise web.HTTPBadRequest()
        if state.lower() == 'true':
            state = True
        elif state.lower() == 'false':
            state = False
        else:
            #TODO LOG
            raise web.HTTPBadRequest()

        influx = request.app["influx-db"]
        await self.pin.set_state(state)
        await self.record_event(influx, state)
        return web.json_response({"state": state})

    async def get_state_request(self, request):
        state = await self.pin.get_state()
        return web.json_response({"state": state})

    async def card_request(self, request):
        influx = request.app["influx-db"]
        last = await self.get_last_event(influx)

        if last is None:
            return web.json_response({
                "name": self.name,
                "error": "unknown state"
            })

        return web.json_response({
            "name": self.name,
            "state": last[1],
            "time": last[0]
        })

    async def event_handler(self, app):
        influx = app["influx-db"]
        
        # Reset GPIO output on start-up to most recent state
        last = await self.get_last_event(influx)
        if last is None:
            state = False
        else:
            state = last[1]
        
        await self.pin.set_state(state)
        await self.record_event(influx, state)
