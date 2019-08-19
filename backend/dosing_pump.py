import asyncio
import datetime
import json

from aiohttp import web 

from .service import Service


class DoseEvent():
    def __init__(self, time, duration):
        self.time = time
        self.duration = duration

    def __lt__(self, other):
        return self.time < other.time

    def serialize(self):
        return {
            "time": self.time.isoformat(),
            "duration": self.duration
        }

    @classmethod
    def load(cls, source):
        return cls(
            time=datetime.time.fromisoformat(source["time"]),
            duration=source["duration"]
        )


class DosingPump(Service):
    def __init__(self, gpio, name):
        super().__init__(name)
        self.gpio = gpio
        self.manual_dose = False
        self.dose_events = []
        self.config = {
            "name": self.name,
            "type": "DosingPump",
            "gpio": self.gpio.id()
        }

        self.add_route(
            web.get('/api/{}/card'.format(self.name), self.card_request),
            web.get('/api/{}/schedule'.format(self.name), self.get_schedule_request),
            web.post('/api/{}/schedule'.format(self.name), self.post_schedule_request),
            web.post('/api/{}/manual'.format(self.name), self.post_manual_request)
        )

    async def card_request(self, request):
        return web.json_response({
            "name": self.name,
            "schedule": [e.serialize() for e in self.dose_events],
            "manual": False if self.manual_dose is False else self.manual_dose.serialize()
        })

    async def get_schedule_request(self, request):
        serialized_events = [event.serialize() for event in self.dose_events]
        return web.json_response(serialized_events)

    async def post_schedule_request(self, request):
        db = request.app["influx-db"]

        content = await request.json()
        dose_events = [DoseEvent.load(event) for event in content]
        self.dose_events = sorted(dose_events)

        serialized_events = [event.serialize() for event in self.dose_events]
        await self.record_event(db, json.dumps(serialized_events))
        return web.json_response(serialized_events)

    async def post_manual_request(self, request):
        if self.manual_dose is not False:
            raise web.HTTPBadRequest()

        content = await request.json()
        self.manual_dose = DoseEvent.load(content)
        return web.json_response(self.manual_dose.serialize())

    def get_next_event(self, time_of_day):
        """Return the next event with a time greater than the current time."""
        for event in self.dose_events:
            if event.time > time_of_day:
                return event

        if len(self.dose_events) > 0:
            return self.dose_events[0]

        return None

    async def dose_duration(self, duration):
        self.log.debug("Executing dose for %d seconds.", duration)
        try:
            await self.gpio.set_state(True)
            await asyncio.sleep(duration)
        finally:
            await self.gpio.set_state(False)
        
    @staticmethod
    def seconds_until(then, now):
        hours = then.hour - now.hour
        minutes = then.minute - now.minute
        seconds = then.second - now.second
        if seconds < 0:
            seconds += 60
            minutes -= 1
        if minutes < 0:
            minutes += 60
            hours -= 1
        if hours < 0:
            hours += 24

        return hours * 60 * 60 + minutes * 60 + seconds

    async def event_handler(self, app):
        self.log.info("Starting event handler.")
        influx = app["influx-db"]

        while not self.shutdown_event.is_set():
            time_of_day = datetime.datetime.now().time()

            if self.manual_dose is not False:
                duration = self.manual_dose.duration
                await self.dose_duration(duration)
                await self.record_event(influx, duration)
                self.manual_dose = False

            next_event = self.get_next_event(time_of_day)
            if next_event is None:
                await asyncio.sleep(10)
                continue

            seconds_until_event = self.seconds_until(next_event.time, time_of_day)
            if seconds_until_event < 15:
                await asyncio.sleep(seconds_until_event)
                await self.dose_duration(next_event.duration)
                await self.record_event(influx, next_event.duration)
            else:
                await asyncio.sleep(10)

        # If the loop is somehow exited, shutdown the pump
        await self.gpio.set_state(False)
        self.log.info("Stopped event handler.")
