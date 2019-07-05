import pytest
import datetime
import asyncio
import asynctest

from aioinflux import InfluxDBClient
from aiohttp import web

from backend.device.gpio import GpioPin
from backend.switch import Switch

TEST_DATABASE = 'test-db'
TEST_NAME = 'test_switch'
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

async def test_switch_get(aiohttp_client, test_app, mock_device):
    switch = Switch(mock_device, TEST_NAME)
    test_app.add_routes(switch.routes())
    client = await aiohttp_client(test_app)

    resp = await client.get("/api/{}".format(TEST_NAME))
    assert resp.status == 200

    content =  await resp.json()
    assert content["name"] == TEST_NAME
    assert content["device"] == mock_device.id.return_value
    
async def test_switch_card(aiohttp_client, test_app, mock_device):
    sensor = Switch(mock_device, TEST_NAME)
    test_app.add_routes(sensor.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    # Does the reply handle no data being present
    resp = await client.get("/api/{}/card".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert content["name"] == TEST_NAME
    assert content["error"] is not None

    # Does the reply return value after one is written
    await sensor.record_event(db, True)
    resp = await client.get("/api/{}/card".format(TEST_NAME))
    assert resp.status == 200
    content =  await resp.json()
    assert content["name"] == TEST_NAME
    assert content["state"] == True
    assert content["time"] > TEST_TIME

async def test_switch_control(aiohttp_client, test_app, mock_device):
    sensor = Switch(mock_device, TEST_NAME)
    test_app.add_routes(sensor.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    resp = await client.post("/api/{}/state".format(TEST_NAME), data={"state": True})
    assert resp.status == 200
    content = await resp.json()
    assert content["state"] == True

    resp = await client.get("/api/{}/state".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert content["state"] == True

    resp = await client.post("/api/{}/state".format(TEST_NAME), data={"state": False})
    assert resp.status == 200
    content = await resp.json()
    assert content["state"] == False

    resp = await client.get("/api/{}/state".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert content["state"] == False

    # Ensure both state change events were recorded in the database
    resp = await client.get("/api/{}/query?events".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert len(content) == 2
