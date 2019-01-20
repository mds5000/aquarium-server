import json
import asyncio
import aiofiles


class JsonDatabase():
    def __init__(self, path: str):
        self.lock = asyncio.Lock()
        self.path = path
        self.database = None

    async def get(self, key, default=None):
        async with self.lock:
            self.database = await self._load_database_from_file()
        return self.database.get(key, default)

    async def update(self, new_dict):
        async with self.lock:
            self.database = await self._load_database_from_file()
            self.database.update(new_dict)
            self._commit()
        return self.database

    async def delete(self, key):
        async with self.lock:
            self.database = await self._load_database_from_file()
            self.database.pop(key)
            self._commit()

    async def _commit(self):
        db_blob = json.dumps(self.database, indent=4)
        async with aiofiles.open(self.path, mode='w') as fd:
            await fd.write(db_blob)

    async def _load_database_from_file(self):
        async with aiofiles.open(self.path, mode='r') as fd:
            data = await fd.read()
            print("DATA:", data)

        if len(data):
            return json.loads(data)
        return {}

