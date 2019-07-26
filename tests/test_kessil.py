import json
import pytest
import datetime
import asyncio
import asynctest

from aioinflux import InfluxDBClient
from aiohttp import web

from backend.device.pwm import PwmPin
from backend.kessil import KessilController, ProfilePoint

TEST_DATABASE = 'test-db'
TEST_NAME = 'test_kessil'
TEST_TIME = int(datetime.datetime.now().timestamp() * 1e9)


@pytest.fixture
async def test_app(loop):
    app = web.Application()
    db = InfluxDBClient(db=TEST_DATABASE, loop=loop)
    app["influx-db"] = db
    return app

@pytest.fixture
def mock_device():
    state = [False]
    def set_mock_state(state_):
        state[0] = state_
        return state[0]
    def get_mock_state():
        return state[0]

    device = asynctest.create_autospec(PwmPin)
    device.id.return_value = "/sys/class/pwm/pwm0"
    device.set_duty_cycle.side_effect = set_mock_state
    device.get_duty_cycle.side_effect = get_mock_state
    return device

async def test_kessil_get(aiohttp_client, test_app, mock_device):
    kessil = KessilController(mock_device, mock_device, TEST_NAME)
    test_app.add_routes(kessil.routes())
    client = await aiohttp_client(test_app)

    resp = await client.get("/api/{}".format(TEST_NAME))
    assert resp.status == 200

    content =  await resp.json()
    assert content["name"] == TEST_NAME
    assert content["spectrum"] == mock_device.id.return_value
    assert content["intensity"] == mock_device.id.return_value
    assert content["profile"] == []
    
async def test_kessil_card(aiohttp_client, test_app, mock_device):
    kessil = KessilController(mock_device, mock_device, TEST_NAME)
    test_app.add_routes(kessil.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    # Does the reply handle no data being present
    resp = await client.get("/api/{}/card".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert content["name"] == TEST_NAME
    assert content["profile"] == []
    assert content["override"] == False

async def test_kessil_profile(aiohttp_client, test_app, mock_device):
    kessil = KessilController(mock_device, mock_device, TEST_NAME)
    test_app.add_routes(kessil.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    # Check for an empty profile
    resp = await client.get("/api/{}/profile".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert len(content) == 0

    # Load a profile
    test_profile = [
        ProfilePoint(datetime.time(1, 30), 20,20).serialize(),
        ProfilePoint(datetime.time(6, 30), 80,80).serialize(),
    ]
    resp = await client.post("/api/{}/profile".format(TEST_NAME),
                             json=test_profile)
    assert resp.status == 200
    content = await resp.json()
    assert len(content) == 2

    # Check that the correct profile was set
    resp = await client.get("/api/{}/profile".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert len(content) == 2
    point_0 = ProfilePoint.load(content[0])
    assert point_0.time == datetime.time(1,30)
    assert point_0.spectrum == 20
    assert point_0.intensity == 20
    point_1 = ProfilePoint.load(content[1])
    assert point_1.time == datetime.time(6,30)
    assert point_1.spectrum == 80
    assert point_1.intensity == 80

async def test_kessil_load_profile(aiohttp_client, test_app, mock_device):
    kessil = KessilController(mock_device, mock_device, TEST_NAME)
    test_app.add_routes(kessil.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    test_profile = [ProfilePoint(datetime.time(3, 30), 30,30).serialize()]
    await kessil.record_event(db, json.dumps(test_profile))

    profile = await kessil.load_profile(db)
    assert len(profile) == 1

async def test_kessil_override(aiohttp_client, test_app, mock_device):
    kessil = KessilController(mock_device, mock_device, TEST_NAME)
    test_app.add_routes(kessil.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    override = ProfilePoint(datetime.time(5, 55), 50,60).serialize()
    resp = await client.post("/api/{}/override".format(TEST_NAME),
                             json=override)
    assert resp.status == 200
    content = await resp.json()
    assert content["time"] == "05:55:00"
    assert content["spectrum"] == 60
    assert content["intensity"] == 50

    resp = await client.get("/api/{}/card".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert content["override"] != False