import asyncio
import datetime

import time

from aiohttp import web 


class DoseEvent():
    def __init__(self, time_of_day, duration):
        self.time = time_of_day
        self.duration = duration

    def __lt__(self, other):
        return self.time < other.time_of_day

    def serialize(self):
        return '{"time":{}, "duration":{}}'.format(self.time, self.duration)


class DosingPump():
    def __init__(self, gpio, name):
        self.name = name
        self.gpio = gpio
        self.dose_events = []

    def set_dosing_events(self, dose_events):
        self.dose_events = sorted(dose_events)

    def get_next_event(self, time_of_day):
        """Return the next event with a time greater than the current time."""
        for event in self.dose_events:
            if event.time > time_of_day:
                return event

        if len(self.dose_events) > 0:
            return self.dose_events[0]

        return None

    async def dose_duration(self, duration):
        try:
            self.gpio.set_state(True)
            await asyncio.get_running_loop().sleep(duration)
        finally:
            self.gpio.set_state(False)
        

    def routes(self):
        return []

    def return_config(self):
        return web.json_request({
            "name": self.name,
            "gpio": self.gpio.path,
            "schedule": [event.serialize() for event in self.dose_events]
        })

    @staticmethod
    def seconds_until(then, now):
        hours = then.hour - now.hour
        if hours < 0:
            hours += 24
        minutes = then.minute - now.minute
        if minutes < 0:
            minutes += 60
            hours -= 1
        seconds = then.second - now.second
        if seconds < 0:
            seconds += 60
            minutes -= 1

        return hours * 60 * 60 + minutes * 60 + seconds

    async def record_event(self, db, state):
        """ Add the event to the database """
        return await db.write({
            "measurement": "events",
            "time": datetime.now(),
            "tags": {"name": self.name},
            "fields": {"value": state}
        })

    async def event_handler(self, app):
        loop = asyncio.get_running_loop()
        influx = app["influx-db"]

        while True:
            time_of_day = datetime.datetime.now().time()
            next_event = self.get_next_event(time_of_day)
            print("ENTER LOOP:", time.time())

            if next_event is None:
                await asyncio.sleep(10)
                continue

            seconds_until_event = self.seconds_until(next_event.time, time_of_day)
            if seconds_until_event < 10:
                await asyncio.sleep(seconds_until_event)
                await self.dose_duration(next_event.duration)
                await self.record_event(db, next_event.duration)

            else:
                await asyncio.sleep(10)

            


