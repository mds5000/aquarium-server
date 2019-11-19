import json
import pytest
import datetime
import asyncio
import asynctest

from aioinflux import InfluxDBClient
from aiohttp import web

from backend.device.gpio import GpioPin
from backend.dosing_pump import DosingPump, DoseEvent

TEST_DATABASE = 'test-db'
TEST_NAME = 'test_dosing_pump'
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

    device = asynctest.create_autospec(GpioPin)
    device.direction.return_value = 'out'
    device.id.return_value = "/sys/class/gpio/pin0"
    device.set_state.side_effect = set_mock_state
    device.get_state.side_effect = get_mock_state
    return device

async def test_dosing_pump_get(aiohttp_client, test_app, mock_device):
    pump = DosingPump(mock_device, TEST_NAME)
    test_app.add_routes(pump.routes())
    client = await aiohttp_client(test_app)

    resp = await client.get("/api/{}".format(TEST_NAME))
    assert resp.status == 200

    content =  await resp.json()
    assert content["name"] == TEST_NAME
    assert content["gpio"] == mock_device.id.return_value
    
async def test_dosing_pump_card(aiohttp_client, test_app, mock_device):
    pump = DosingPump(mock_device, TEST_NAME)
    test_app.add_routes(pump.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    resp = await client.get("/api/{}/card".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert content["name"] == TEST_NAME
    assert content["schedule"] == []
    assert content["calibration"] == 1.66

async def test_dosing_schedule(aiohttp_client, test_app, mock_device):
    pump = DosingPump(mock_device, TEST_NAME)
    test_app.add_routes(pump.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    # Check for an empty profile
    resp = await client.get("/api/{}/schedule".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert len(content) == 0

    # Load a dosing schedule
    test_profile = [
        DoseEvent(datetime.time(1, 30), 2).serialize(),
        DoseEvent(datetime.time(6, 30), 8).serialize(),
    ]
    resp = await client.post("/api/{}/schedule".format(TEST_NAME),
                             json=test_profile)
    assert resp.status == 200
    content = await resp.json()
    assert len(content) == 2

    # Check that the correct schedule was set
    resp = await client.get("/api/{}/schedule".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert len(content) == 2
    event_0 = DoseEvent.Load(content[0])
    assert event_0.time == datetime.time(1,30)
    assert event_0.duration == 2
    event_1 = DoseEvent.Load(content[1])
    assert event_1.time == datetime.time(6,30)
    assert event_1.duration == 8

async def test_manual_dose(aiohttp_client, test_app, mock_device):
    pump = DosingPump(mock_device, TEST_NAME)
    test_app.add_routes(pump.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    event = DoseEvent(datetime.time(), 5).serialize()
    resp = await client.post("/api/{}/manual".format(TEST_NAME),
                             json=event)
    assert resp.status == 200
    content = await resp.json()
    assert content["volume"] == None
    assert content["duration"] == 5

    #TODO Test that a manual dose is recorded and a 'purge' is not recorded.
