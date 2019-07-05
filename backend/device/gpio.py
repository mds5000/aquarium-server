import aiofiles
import asyncio
import os.path

class GpioPin():
    def __init__(self, number, direction="out", root="/sys/class/gpio"):
        """
        """
        self.path = os.path.join(root, "gpio{}".format(number))
        if not os.path.exists(self.path):
            self._export_gpio(root, number)
        self._set_direction(direction)
    
    def _export_gpio(self, root, pin):
        with open(os.path.join(root, "export"), 'w') as export:
            export.write("{}\n".format(pin))
        if not os.path.exists(self.path):
            raise RuntimeError("Could not export GPIO: '{}'".format(self.path))

    def _set_direction(self, direction):
        if direction not in ["in", "out"]:
            raise ValueError("GPIO direction must be one of 'in' or 'out', not '{}'".format(direction))

        self._direction = direction
        with open(os.path.join(self.path, "direction"), 'w') as gpio:
            gpio.write(direction)
    
    def direction(self):
        return self._direction

    def id(self):
        return self.path

    async def set_state(self, state):
        state = '1' if state else '0'
        async with aiofiles.open(os.path.join(self.path, "value"), 'w') as gpio:
            await gpio.write(state)

    async def get_state(self):
        async with aiofiles.open(os.path.join(self.path, "value"), 'r') as gpio:
            state = await gpio.read()
        return state[0] == '1'