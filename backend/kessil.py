import asyncio
import datetime

from aiohttp import web 
from aioinflux import InfluxDBClient


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

        intensity = (self.intensity * time_until + next.intensity * time_since) / time_delta
        spectrum = (self.spectrum * time_until + next.spectrum * time_since) / time_delta

        return ProfilePoint(time_of_day, intensity, spectrum)


class KessilController():
    def __init__(self, spectrum, intensity, name):
        self.spectrum = spectrum
        self.intensity = intensity
        self.name = name   
        self.profile = [
            ProfilePoint(datetime.time(5, 50, 0), 1, 0),
            ProfilePoint(datetime.time(5, 55, 0), 1, 1),
            ProfilePoint(datetime.time(6, 15, 0), 1, 0),
            ProfilePoint(datetime.time(6, 16, 0), 0, 1),
        ]

    def set_profile(self, points):
        self.profile = sorted(points)

    def routes(self):
        return [
            web.get('/api/{}'.format(self.name), self.get_request),
            web.get('/api/{}/value'.format(self.name), self.value_request),
            web.get('/api/{}/card'.format(self.name), self.card_request)
        ]

    def return_config(self):
        return web.json_response({
            "name": self.name,
            "spectrum": self.spectrum.path,
            "intensity": self.intensity.path,
            "schedule": [event.serialize() for event in self.profile]
        })

    async def record_event(self, db, state):
        """ Add the event to the database """
        return await db.write({
            "measurement": "events",
            "time": datetime.datetime.now(),
            "tags": {"name": self.name},
            "fields": {
                "intensity": state.intensity, 
                "spectrum": state.spectrum 
            }
        })

    def get_prev_event(self, time_of_day):
        """Return the last event with a time less than the current time."""
        for event in reversed(self.profile):
            if event.time < time_of_day:
                return event

        if len(self.profile) > 0:
            return self.profile[0]

        return None

    def get_next_event(self, time_of_day):
        """Return the next event with a time greater than the current time."""
        for event in self.profile:
            if event.time > time_of_day:
                return event

        if len(self.profile) > 0:
            return self.profile[0]

        return None

    async def get_request(self, request):
        return self.return_config()

    async def value_request(self, request):
        spectrum = await self.spectrum.get_duty_cycle()
        intensity = await self.intensity.get_duty_cycle()

        return web.json_response({
            "time": datetime.datetime.now().time().isoformat(),
            "spectrum": spectrum,
            "intensity": intensity
        })

    async def card_request(self, request):
        return web.json_response({
            "type": "kessil",
            "name": self.name,
            "profile": [p.serialize() for p in self.profile]
        })

    async def event_handler(self, app):
        loop = asyncio.get_running_loop()
        influx = app["influx-db"]

        while True:
            time_of_day = datetime.datetime.now().time()
            next_event = self.get_next_event(time_of_day)
            prev_event = self.get_prev_event(time_of_day)

            if next_event is None:
                await asyncio.sleep(10)
                continue

            else:
                await asyncio.sleep(1)
                interp = prev_event.interpolate(next_event, time_of_day)
                await self.spectrum.set_duty_cycle(interp.spectrum)
                await self.intensity.set_duty_cycle(interp.intensity)

                if ProfilePoint.seconds_until(time_of_day, prev_event.time) == 0:
                    print("Complteted POINT:", interp)
                    await self.record_event(influx, interp)


            