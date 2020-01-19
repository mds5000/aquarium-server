import pytest
import datetime
import asyncio
import asynctest

from aioinflux import InfluxDBClient
from aiohttp import web

from backend.device.hwmon import HwmonDevice
from backend.sensor import AnalogSensor

TEST_DATABASE = 'test-db'
TEST_NAME = 'test_sensor'
TEST_TIME = int(datetime.datetime.now().timestamp() * 1e9)


@pytest.fixture
async def test_app(loop):
    app = web.Application()
    db = InfluxDBClient(db=TEST_DATABASE, loop=loop)
    app["influx-db"] = db
    return app

@pytest.fixture
def mock_device():
    device = asynctest.create_autospec(HwmonDevice)
    device.read_value.return_value = 42.0
    device.id.return_value = "/sys/class/hwmon/hwmon0/mock_sensor"
    device.get_calibration.return_value = (1.0, 0.0)
    return device

async def test_sensor_get(aiohttp_client, test_app, mock_device):
    test_period = 45
    sensor = AnalogSensor(mock_device, TEST_NAME, test_period)
    test_app.add_routes(sensor.routes())
    client = await aiohttp_client(test_app)

    resp = await client.get("/api/{}".format(TEST_NAME))
    assert resp.status == 200

    content =  await resp.json()
    assert content["name"] == TEST_NAME
    assert content["sensor"] == mock_device.id.return_value
    assert content["period"] == test_period
    
async def test_sensor_card(aiohttp_client, test_app, mock_device):
    sensor = AnalogSensor(mock_device, TEST_NAME)
    test_app.add_routes(sensor.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)

    client = await aiohttp_client(test_app)

    # Does the reply handle no data being present
    resp = await client.get("/api/{}/card".format(TEST_NAME))
    assert resp.status == 503

    # Does the reply return value after one is written
    await sensor.record_sample(db, TEST_NAME, 42)
    resp = await client.get("/api/{}/card".format(TEST_NAME))
    assert resp.status == 200
    content =  await resp.json()
    assert content["name"] == TEST_NAME
    assert content["value"] == 42
#    assert content["time"] > TEST_TIME

    # Does the reply return the latest value
    await sensor.record_sample(db, TEST_NAME, 43)
    resp = await client.get("/api/{}/card".format(TEST_NAME))
    assert resp.status == 200
    content =  await resp.json()
    assert content["name"] == TEST_NAME
    assert content["value"] == 43
#    assert content["time"] > TEST_TIME

async def test_sensor_query(aiohttp_client, test_app, mock_device):
    sensor = AnalogSensor(mock_device, TEST_NAME)
    test_app.add_routes(sensor.routes())
    db = test_app["influx-db"]
    await db.drop_database(db=TEST_DATABASE)
    await db.create_database(db=TEST_DATABASE)
    await sensor.record_sample(db, TEST_NAME, 1)
    await sensor.record_sample(db, TEST_NAME, 3)
    await sensor.record_sample(db, TEST_NAME, 5)

    client = await aiohttp_client(test_app)

    # Query returning all data
    resp = await client.get("/api/{}/query".format(TEST_NAME))
    assert resp.status == 200
    content = await resp.json()
    assert len(content) == 3