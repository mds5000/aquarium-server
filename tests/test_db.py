import pytest
import tempfile
from json.decoder import JSONDecodeError

from backend.db import JsonDatabase


@pytest.mark.asyncio
async def test_load_data():
    """Verify json can be loaded from a file"""
    with tempfile.NamedTemporaryFile() as tempfd:
        tempfd.write(b'{"key":"value"}')
        tempfd.flush()

        database = JsonDatabase(tempfd.name)
        assert await database.get("key") == "value"

@pytest.mark.asyncio
async def test_load_corrupt_data():
    """Verify corrupt json throws exception"""
    with tempfile.NamedTemporaryFile() as tempfd:
        tempfd.write(b'{"key":::"value"}')
        tempfd.flush()

        database = JsonDatabase(tempfd.name)
        with pytest.raises(JSONDecodeError):
            await database.get("key")