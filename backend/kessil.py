import asyncio
import json
import datetime
import logging

from aiohttp import web 

from .service import Service


logger = logging.getLogger(__name__)


class ProfilePoint():
    def __init__(self, time, intensity, spectrum):
        self.time = time
        self.intensity = intensity
        self.spectrum = spectrum

    def __lt__(self, other):
        return self.time < other.time

    def __repr__(self):
        return "<ProfilePoint {}/{}/{}>".format(self.time, self.intensity, self.spectrum)

    def serialize(self):
        return {
            "time": self.time.isoformat(),
            "spectrum": self.spectrum,
            "intensity": self.intensity
        }
    
    @classmethod
    def load(cls, source):
        return cls(
            time=datetime.time.fromisoformat(source["time"]),
            intensity=float(source["intensity"]),
            spectrum=float(source["spectrum"])
        )

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

    def interpolate(self, next, time_of_day):
        time_delta = self.seconds_until(next.time, self.time)
        time_until = self.seconds_until(next.time, time_of_day)
        time_since = self.seconds_until(time_of_day, self.time)

        if time_delta == 0:
            return self

        intensity = (self.intensity * time_until + next.intensity * time_since) / time_delta
        spectrum = (self.spectrum * time_until + next.spectrum * time_since) / time_delta

        return ProfilePoint(time_of_day, intensity, spectrum)


class KessilController(Service):
    def __init__(self, spectrum_pwm, intensity_pwm, name):
        super().__init__(name)
        self.spectrum = spectrum_pwm
        self.intensity = intensity_pwm
        self.profile = []
        self.override = False
        self.config = {
            "name": self.name,
            "type": "KessilController",
            "spectrum": self.spectrum.id(),
            "intensity": self.intensity.id()
        }

        self.add_route(
            web.get('/api/{}/card'.format(self.name), self.card_request),
            web.get('/api/{}/profile'.format(self.name), self.get_profile_request),
            web.post('/api/{}/profile'.format(self.name), self.post_profile_request),
            web.post('/api/{}/override'.format(self.name), self.post_override_request)
        )

    async def card_request(self, request):
        return web.json_response({
            "name": self.name,
            "profile": [p.serialize() for p in self.profile],
            "override": False if self.override is False else self.override.serialize()
        })

    async def get_profile_request(self, request):
        serialized_points = [point.serialize() for point in self.profile]
        return web.json_response(serialized_points)

    async def post_profile_request(self, request):
        """ Updated the daily Kessil Profile.

        Json Body:
        [
            {"time":"15:00:00", "spectrum": 0.3, "intensity": 0.66},
            { ... }
        ]

        """
        #TODO: Handle invalid JSON/bad payload gracefully w/ error message
        db = request.app["influx-db"]
        profile = await request.json()
        self.log.debug("Profile update requested: %r", profile)

        if len(profile) == 0:
            raise web.HTTPBadRequest()

        profile_points = [ProfilePoint.load(point) for point in profile]
        self.profile = sorted(profile_points)

        serialized_points = [point.serialize() for point in self.profile]
        await self.record_event(db, "profile", json.dumps(serialized_points))
        self.log.info("Updated Kessil profile: %s", json.dumps(serialized_points))

        return web.json_response(serialized_points)

    async def post_override_request(self, request):
        override_value = await request.json()
        self.override = ProfilePoint.load(override_value)
        self.log.info("User override of light settings: Spec. %d%%, Inten. %d%%.",
                      self.override.spectrum * 100,
                      self.override.intensity * 100)
        await self.spectrum.set_duty_cycle(self.override.spectrum)
        await self.intensity.set_duty_cycle(self.override.intensity)

        loop = asyncio.get_running_loop()
        time_of_day = datetime.datetime.now().time()
        cancel_delay = ProfilePoint.seconds_until(self.override.time, time_of_day)
        self.log.info("  override expires in %d seconds", cancel_delay)

        def cancel_override(self):
            self.override = False
            self.log.info("User override expired.")
        loop.call_later(cancel_delay, cancel_override, self)

        return web.json_response(self.override.serialize())


    def _prev_event(self, time_of_day):
        """Return the last event with a time less than the current time."""
        for event in reversed(self.profile):
            if event.time < time_of_day:
                return event

        if len(self.profile) > 0:
            return self.profile[0]

        return None

    def _next_event(self, time_of_day):
        """Return the next event with a time greater than the current time."""
        for event in self.profile:
            if event.time > time_of_day:
                return event

        if len(self.profile) > 0:
            return self.profile[0]

        return None

    async def load_profile(self, db):
        try:
            _, profile = await self.get_last(db, "profile")
            profile = json.loads(profile)
            profile_points = [ProfilePoint.load(point) for point in profile]
            return sorted(profile_points)
        except:
            return []

    async def event_handler(self, app):
        self.log.info("Starting event handler.")

        influx = app["influx-db"]
        self.profile = await self.load_profile(influx)
        self.log.info("Loaded profile from database; %d points loaded.", len(self.profile))

        while not self.shutdown_event.is_set():
            time_of_day = datetime.datetime.now().time()

            if self.override is not False:
                await asyncio.sleep(1)
                continue

            next_event = self._next_event(time_of_day)
            prev_event = self._prev_event(time_of_day)
            if next_event is None:
                await asyncio.sleep(1)
                continue

            interp = prev_event.interpolate(next_event, time_of_day)
            await self.spectrum.set_duty_cycle(interp.spectrum)
            await self.intensity.set_duty_cycle(interp.intensity)
            await asyncio.sleep(1)

        self.log.info("Stopped event handler.")