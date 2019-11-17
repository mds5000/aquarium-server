import asyncio
import logging
from datetime import datetime

from aiohttp import web 
from aioinflux import InfluxDBClient


class Service():
    def __init__(self, name):
        self.log = logging.getLogger("Service<{}>".format(name))
        self.name = name
        self.shutdown_event = asyncio.Event()
        self.config = {
            "name": self.name,
            "type": "UnknownService"
        }
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

    async def record_data(self, db, key, value, time=None, **tags):
        if time is None:
            time = datetime.now()
        tags["service"] = self.name
        return await db.write({
            "measurement": "records",
            "time": time,
            "tags": tags,
            "fields": {key: value}
        })

    def record_sample(self, db, name, value, **tags):
        tags["kind"] = "sample"
        return self.record_data(db, name, value, **tags)

    def record_event(self, db, name, value, **tags):
        """ Add the event to the database """
        tags["kind"] = "event"
        return self.record_data(db, name, value, **tags)

    async def get_request(self, request):
        """ Returns the configuration of the sensor """
        return web.json_response(self.config)

    async def query_request(self, request):
        """Returns the values from the database for this sensor

        # TODO: Implement these parameters
        URL Parameters:
            - "events": Add this parameter to query the events database
            - "begin": Return Data after this time
            - "end": Return Data before this time

        Returs 404 if no data exists.
        """
        influx = request.app["influx-db"]
        selection = request.query.get("select", "*")
        #TODO: Sanitize inputs...
        resp = await influx.query("""SELECT {selection} FROM "records" WHERE "service"='{name}'"""
                                  .format(selection=selection, name=self.name))
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

    async def get_last(self, db, key):
        resp = await db.query(
            """SELECT LAST("{key}") FROM "records" WHERE "service"='{name}'"""
            .format(key=key, name=self.name)
        )
        try:
            result= resp["results"][0]
            series = result["series"][0]
            time, value = series["values"][0]
            return (time, value)
        except KeyError:
            return None

    async def event_handler(self, app):
        pass