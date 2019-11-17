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
    def Load(cls, source):
        return cls(
            time=datetime.time.fromisoformat(source["time"]),
            duration=float(source["duration"])
        )
    
    @classmethod
    def Now(cls, duration):
        return cls(
            time=datetime.time(),
            duration=float(duration)
        )


class DosingPump(Service):
    def __init__(self, gpio, name):
        super().__init__(name)
        self.gpio = gpio
        self.dose_events = []
        self.calibration = 1.66 # mL / Second
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
            "calibration": self.calibration
        })

    async def get_schedule_request(self, request):
        serialized_events = [event.serialize() for event in self.dose_events]
        return web.json_response(serialized_events)

    async def post_schedule_request(self, request):
        db = request.app["influx-db"]

        content = await request.json()
        self.log.debug("Dosing update requested: %r", content)
        dose_events = [DoseEvent.Load(event) for event in content]
        self.dose_events = sorted(dose_events)

        serialized_events = [event.serialize() for event in self.dose_events]
        await self.record_event(db, "schedule", json.dumps(serialized_events))
        self.log.info("Updated dosing schedule: %s", json.dumps(serialized_events))

        return web.json_response(serialized_events)

    async def post_manual_request(self, request):
        """ Handle a manual dose event request.
        
        Expects JSON request:
        {
            "duration": [float] seconds to dose
            "volume": [float] mL to dose
            "purge": [bool] if true, don't record the event
        }
        Only one of 'duration' or 'volume' should be included.

        Raises: HTTPBadRequest on invalid or missing payload.
        """
        db = request.app["influx-db"]
        content = await request.json()
        purge = content.get("purge", False)

        duration = 0
        duration = content.get("duration")
        volume = content.get("volume")
        if volume is not None:
            volume = float(volume)
            duration = volume / self.calibration

        if duration is None and volume is None:
            raise web.HTTPBadRequest()

        duration = float(duration)
        if purge:
            asyncio.create_task(self.dose_duration(duration))
        else:
            asyncio.create_task(self.record_dose(duration, db))

        return web.json_response({"duration": duration, "volume": volume})

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

    async def record_dose(self, duration, db):
        await self.dose_duration(duration)
        await self.record_event(db, "dose", duration)
        
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

    async def load_schedule(self, db):
        try:
            _, schedule = await self.get_last(db, "schedule")
            schedule = json.loads(schedule)
            schedule = [DoseEvent.Load(event) for event in schedule]
            return sorted(schedule)
        except:
            return []

    async def event_handler(self, app):
        self.log.info("Starting event handler.")
        influx = app["influx-db"]
        self.dose_events = await self.load_schedule(influx)
        self.log.info("Loaded dose schedule from database; %d events loaded.", len(self.dose_events))

        while not self.shutdown_event.is_set():
            time_of_day = datetime.datetime.now().time()

            next_event = self.get_next_event(time_of_day)
            if next_event is None:
                await asyncio.sleep(10)
                continue

            seconds_until_event = self.seconds_until(next_event.time, time_of_day)
            if seconds_until_event < 15:
                await asyncio.sleep(seconds_until_event)
                await self.record_dose(next_event.duration, influx)
            else:
                await asyncio.sleep(10)

        # If the loop is somehow exited, shutdown the pump
        await self.gpio.set_state(False)
        self.log.info("Stopped event handler.")
