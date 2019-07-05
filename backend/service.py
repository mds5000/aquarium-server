import asyncio
from datetime import datetime

from aiohttp import web 
from aioinflux import InfluxDBClient


class Service():
    def __init__(self, name):
        self.name = name
        self.shutdown_event = asyncio.Event()
        self.config = web.json_response({
            "name": self.name
        })
        self._routes = [
            web.get('/api/{}'.format(self.name), self.get_request),
            web.get('/api/{}/query'.format(self.name), self.query_request)
        ]

    def add_route(self, *routes):
        self._routes += routes

    def routes(self):
        return self._routes

    def shutdown(self):
        self.shutdown_event.set()

    async def record_data(self, db, measurement, value, time=None):
        if time is None:
            time = datetime.now()
        return await db.write({
            "measurement": measurement,
            "time": time,
            "tags": {"name": self.name},
            "fields": {"value": value}
        })

    def record_sample(self, db, value):
        return self.record_data(db, "samples", value)

    def record_event(self, db, state):
        """ Add the event to the database """
        return self.record_data(db, "events", state)

    async def get_request(self, request):
        """ Returns the configuration of the sensor """
        return self.config

    async def query_request(self, request):
        """Returns the values from the database for this sensor

        # TODO: Implement these parameters
        URL Parameters:
            - "events": Add this parameter to query the events database
            - "begin": Return Data after this time
            - "end": Return Data before this time

        Returs 404 if no data exists.
        """
        measurement = 'events' if request.query.get("events") is not None else 'samples'
        influx = request.app["influx-db"]
        resp = await influx.query("""SELECT value FROM "{measurement}" WHERE "name"='{name}'"""
                                  .format(measurement=measurement, name=self.name))
        try:
            result= resp["results"][0]
            series = result["series"][0]
            values = series["values"]
        except KeyError:
            raise web.HTTPNotFound()
        return web.json_response(values)
        """
        begin = request.query.get("begin")
        start_condition = "" if begin is None else "AND time >= {}".format(begin)

        end = request.query.get("end")
        end_condition = "" if end is None else "AND time < {}".format(end)

        influx = request.app["influx-db"]
        resp = await influx.query(
            ""
            SELECT value FROM "events" 
            WHERE "name"='{name}' {start} {end}
            "".format(name=self.name, start=start_condition, end=end_condition)
        )
        """

    async def get_last(self, db, measurement):
        resp = await db.query(
            """SELECT LAST("value") FROM "{measurement}"
               WHERE "name"='{name}'
            """.format(measurement=measurement, name=self.name)
        )
        try:
            result= resp["results"][0]
            series = result["series"][0]
            time, value = series["values"][0]
            return (time, value)
        except KeyError:
            return None

    def get_last_sample(self, db):
        return self.get_last(db, "samples")

    def get_last_event(self, db):
        return self.get_last(db, "events")

    async def event_handler(self, app):
        pass