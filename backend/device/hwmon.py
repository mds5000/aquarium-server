import asyncio
import os.path
import aiofiles


class HwmonDevice():
    def __init__(self,
                 device,
                 root="/sys/class/hwmon/hwmon0",
                 calibration=(0.001, 0)):
        self.path = os.path.join(root, device)
        if not os.path.exists(self.path):
            raise ValueError("Could not find sensor in '{}'".format(self.path))
        self.calibration = calibration

    def id(self):
        return self.path

    async def read_value(self):
        async with aiofiles.open(self.path, 'r') as sensor:
            temp = await sensor.readline()
        (m, b) = self.calibration
        return int(temp) * m + b

    def set_calibration(self, m, b):
        self.calibration = (m, b)

    def get_calibration(self):
        return self.calibration