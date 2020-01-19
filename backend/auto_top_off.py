import asyncio
import datetime
import json

from aiohttp import web 

from .service import Service

class AtoState:
    DISABLED = 0 # ATO is disabled, not sensing
    MONITOR = 1  # Full, waiting for trip
    WINDOW = 2   # Tripped, waiting on debounce window
    FILLING = 3  # Filling, waiting on clear or timeout

class DosingPump(Service):
    def __init__(self, sensor, pump, name):
        super().__init__(name)
        self.sensor = sensor
        self.pump = pump
        self.current_state = AtoState.DISABLED
        self.config = {
            "name": self.name,
            "type": "AutoTopOff",
            "sensor": self.sensor.id(),
            "pump": self.pump.id()
        }

        self.add_route(
            web.get('/api/{}/card'.format(self.name), self.card_request),
            web.post('/api/{}/state'.format(self.name), self.post_state_request)
        )

    async def card_request(self, request):
        return web.json_response({
            "name": self.name,
            "paused": "EN/PAUS/DIS state",
            "sensor_state": "SNEOSR",
            "last_fill": "DATETIME OF LAST FILL",
            "last_24hrs": "AMOUNT DOSED"
        })

    async def post_state_request(self, request):
        db = request.app["influx-db"]
        self.record_event(db, "state", AtoState.DISABLED, {"reason": "post request"})
        return web.json_response({
            "name": self.name,
            "state": self.current_state
        })


    def load_state():

    async def event_handler(self, app):
        self.log.info("Starting event handler.")
        influx = app["influx-db"]
        loop = asyncio.get_running_loop()
        self.current_state = self.load_state():


        transition_time = 0.0
        while not self.shutdown_event.is_set():
            asyncio.sleep(0.5)

            if self.current_state == AtoState.DISABLED:
                self.pump.set_state(False)

            elif self.current_state == AtoState.MONITOR:
                if self.sensor.get_state():
                    transition_time = loop.time()
                    self.current_state = AtoState.WINDOW

            elif self.current_state == AtoState.WINDOW:
                if not self.sensor.get_state():
                    self.current_state = AtoState.MONITOR

                elif loop.time() > (transition_time + self.window_period):
                    transition_time = loop.time()
                    self.current_state = AtoState.FILLING
                    self.pump.set_state(True)

            elif self.current_state == AtoState.FILLING:
                fill_time = loop.time() - transition_time
                if not self.sensor.get_state():
                    # Full, go back to monitoring
                    self.current_state = AtoState.MONITOR

                elif (fill_time >= self.autofill_timeout):
                    # Timeout without reaching full
                    self.current_state = AtoState.DISABLED
                    self.log.error("ATO Timeout while filling. ATO Disabled.")

                transition_time = loop.time()
                self.pump.set_state(False)
                self.record_sample(db, "fill", fill_time)

            else:
                # Invalid state, go back to monitoring
                self.pump.set_state(False)
                self.current_state = AtoState.MONITOR

        # If the loop is somehow exited, shutdown the pump
        await self.pump.set_state(False)
        self.log.info("Stopped event handler.")
