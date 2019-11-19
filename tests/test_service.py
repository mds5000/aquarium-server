import pytest
import datetime
import asyncio
import asynctest

from aioinflux import InfluxDBClient
from aiohttp import web

from backend.service import Service

TEST_DATABASE = 'test-db'
TEST_NAME = 'test_service'
TEST_TIME = int(datetime.datetime.now().timestamp() * 1e9)
TEST_DATA = [
    [datetime.datetime(2016, 12, 12), 'x', 1],
    [datetime.datetime(2017, 12, 12), 'x', 2],
    [datetime.datetime(2018, 12, 12), 'x', 3],
    [datetime.datetime(2019, 8, 1, 0), 'y', 1],
    [datetime.datetime(2019, 8, 1, 1), 'y', 2],
    [datetime.datetime(2019, 8, 1, 2), 'y', 3],
    [datetime.datetime(2019, 8, 1, 3), 'y', 4]
]


@pytest.fixture
async def test_app(loop):
    app = web.Application()
    db = InfluxDBClient(db=TEST_DATABASE, loop=loop)
    app["influx-db"] = db
    return app

async def test_request(aiohttp_client, test_app):
    service = Service(TEST_NAME)
    test_app.add_routes(service.routes())
    client = await aiohttp_client(test_app)

    resp = await client.get("/api/{}".format(TEST_NAME))
    assert resp.status == 200

    content =  await resp.json()
    assert content["name"] == TEST_NAME
    assert content["type"] == "UnknownService"
    
async def test_query(aiohttp_client, test_app):
    service = Service(TEST_NAME)
    test_app.add_routes(service.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    # Load test data
    for date, key, val in TEST_DATA:
        await service.record_data(db, key, val, time=date, kind="sample")

    # By Default get last 24 hours, which should be empty
    resp = await client.get("/api/{}/query".format(TEST_NAME))
    assert resp.status == 404
    #content = await resp.json()
    #print(content)

    # Add a recent value to the DB
    await service.record_sample(db, 'x', 100)

    # Repeat the default query, expecting the singl data point above
    resp = await client.get("/api/{}/query".format(TEST_NAME))
    assert resp.status == 200
    content =  await resp.json()
    assert len(content) == 1
    assert content[0]["x"] == 100
    assert content[0]["kind"] == "sample"

async def test_query_selection(aiohttp_client, test_app):
    service = Service(TEST_NAME)
    test_app.add_routes(service.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    # Load test data
    for date, key, val in TEST_DATA:
        await service.record_data(db, key, val, time=date, kind="sample")
    await service.record_sample(db, 'x', 100)

    # Test default selection, returns all keys with a value in the given range
    resp = await client.get("/api/{}/query".format(TEST_NAME))
    assert resp.status == 200
    content =  await resp.json()
    assert len(content) == 1
    assert content[0]["x"] == 100
    assert "y" not in content[0]

    # Test selection parameter, return just the value selected
    resp = await client.get("/api/{}/query?select=x".format(TEST_NAME))
    assert resp.status == 200
    content =  await resp.json()
    assert len(content) == 1
    assert content[0]["x"] == 100
    assert "y" not in content[0]
    
    # Test selection parameter, return the keys selected even if empty
    resp = await client.get("/api/{}/query?select=x,y".format(TEST_NAME))
    assert resp.status == 200
    content =  await resp.json()
    assert len(content) == 1
    assert content[0]["x"] == 100
    assert content[0]["y"] == None

async def test_query_range(aiohttp_client, test_app):
    service = Service(TEST_NAME)
    test_app.add_routes(service.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    # Load test data
    for date, key, val in TEST_DATA:
        await service.record_data(db, key, val, time=date, kind="sample")

    # Test default selection, returns all keys with a value in the given range
    resp = await client.get("/api/{}/query?begin=2019-01-01".format(TEST_NAME))
    assert resp.status == 200
    content =  await resp.json()
    assert len(content) == 4

    # Test default selection, returns all keys with a value in the given range
    resp = await client.get("/api/{}/query?begin=2017-01-01&end=2019-01-01".format(TEST_NAME))
    assert resp.status == 200
    content =  await resp.json()
    assert len(content) == 2

