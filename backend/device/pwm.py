import asyncio
import aiofiles
import os.path

class PwmPin():
    def __init__(self, channel, period=1000000, root="/sys/class/pwm"):
        """
        """
        self.path = os.path.join(root, "pwm{}".format(channel))
        if not os.path.exists(self.path):
            raise RuntimeError("PWM Channel not available, is 'pwm-2chan' added to /boot/config.txt")

        self._initialize_pwm(period)
    
    def _initialize_pwm(self, period):
        self.period = period / 1.0e9
        with open(os.path.join(self.path, "enable"), 'w') as enable:
            enable.write("1")
        with open(os.path.join(self.path, "period"), 'w') as period_file:
            period_file.write(str(period))

    def id(self):
        return self.path

    async def set_duty_cycle(self, duty_cycle):
        duty = int(duty_cycle * self.period * 1e9)
        async with aiofiles.open(os.path.join(self.path, "duty_cycle"), 'w') as dc_file:
            await dc_file.write(str(duty))

    async def get_duty_cycle(self):
        async with aiofiles.open(os.path.join(self.path, "duty_cycle"), 'r') as dc_file:
            duty_cycle = await dc_file.read()
        return float(duty_cycle) / (self.period * 1e9)
