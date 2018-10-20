import os
import tempfile

import pytest

from backend.app import app, db, mqtt
from backend.schema import init_test_data

@pytest.fixture
def client():
    db_file, path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+path

    with app.app_context():
        db.create_all()
        init_test_data(app)

    client = app.test_client()

    yield client

    os.close(db_file)
    os.unlink(path)


def test_devices_api(client):
    resp = client.get('/api/devices').get_json()
    assert len(resp) == 2

    assert resp[0]['id'] == 1
    assert resp[0]['address'] == 'test/device1'
    assert resp[0]['name'] == 'test/device1'
    assert resp[0]['description'] == "A short description"
    assert resp[0]['units'] == None

    assert resp[1]['id'] == 2
    assert resp[1]['address'] == 'test/device2'
    assert resp[1]['name'] == 'My Device'
    assert resp[1]['description'] == "A longer description"
    assert resp[1]['units'] == 'Fish'

def test_post_device_api(client):
    resp = client.post("/api/device/1", json={"id": 7, "name": "new_name"}).get_json()

    assert resp["id"] == 1
    assert resp['address'] == 'test/device1'
    assert resp['name'] == 'new_name'
    assert resp['description'] == "A short description"
    assert resp['units'] == None

def test_delete_device_api(client):
    resp = client.delete("/api/device/1")
    assert resp.data == "1"

    resp = client.get('/api/devices').get_json()
    assert len(resp) == 1


def test_events_api(client):
    resp = client.get('/api/events').get_json()
    assert len(resp) == 0



    # Test get Events

    # Test create Event

    # Test delete Event


