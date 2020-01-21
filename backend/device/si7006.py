import fcntl
import os
import logging
import struct
import asyncio

IOCTL_I2C_SLAVE = 0x0703


class Si7006Temperature():
    def __init__(self, path):
        self.log = logging.getLogger("Device<Si7006/Temp>")
        self.fd = os.open(path, os.O_RDWR)
        fcntl.ioctl(self.fd, IOCTL_I2C_SLAVE, 0x40)

    def id(self):
        return "si7006/temp"

    async def read_value(self):
        try:
            os.write(self.fd, b"\xF3")
            await asyncio.sleep(1)
            b, = struct.unpack(">H", os.read(self.fd, 2))
            t = ((b * 175.72) / 65536.0) - 46.85
            f = t * 1.8 + 32
            return f
        except OSError as e:
            self.log.error("Failed to read value: %s", str(e))
            return 0.0


class Si7006Humidity():
    def __init__(self, path):
        self.log = logging.getLogger("Device<Si7006/Humidity>")
        self.fd = os.open(path, os.O_RDWR)
        fcntl.ioctl(self.fd, IOCTL_I2C_SLAVE, 0x40)

    def id(self):
        return "si7006/humidity"

    async def read_value(self):
        try:
            await asyncio.sleep(1)
            os.write(self.fd, b"\xF5")
            await asyncio.sleep(1)
            data, = struct.unpack(">H", os.read(self.fd, 2))
            humidity = ((data * 125.0) / 65536.0) - 6
            return humidity
        except OSError as e:
            self.log.error("Failed to read value: %s", str(e))
            return 0.0


