"""
Emulates a 1-wire D18S20 temp sensor.


"""

import os.path
import tempfile

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class MockTempSensor():
    """
    Creates the following files.
        /hwmon0/device/name   - The name of the hwmon device
        /hwmon0/temp1_input   - Temperature (in milliCelcius)
    """
    def __init__(self):
        """Create a mock temperature sensor at the given root path"""
        self.temp_dir = tempfile.TemporaryDirectory()

        self.root = self.temp_dir.name
        os.makedirs(os.path.join(self.root, "hwmon0", "device"))
        with open(os.path.join(self.root, "hwmon0", "temp1_input"), "w") as f:
            f.write("25000")

        with open(os.path.join(self.root, "hwmon0", "device", "name"), "w") as f:
            f.write("28-ABCDEFG")
            print(f.name)

    def cleanup(self):
        os.remove(os.path.join(self.root, "hwmon0", "temp1_input"))
        os.remove(os.path.join(self.root, "hwmon0", "device", "name"))
        os.removedirs(os.path.join(self.root, "hwmon0"))
        self.temp_dir.cleanup()

    def update_temperature(self, temperature):
        """Update the file with the provided temperature."""
        with open(os.path.join(self.root, "hwmon0", "temp1_input"), "w") as f:
            f.write(str(temperature))

    def readback_temperature(self):
        """Return the temperature writtine to the file."""
        with open(os.path.join(self.root, "hwmon0", "temp1_input"), "w") as f:
            return int(f.readline().strip())


class MockPwmChannel(FileSystemEventHandler):
    """

    Creates the following files:
        /pwm0/period        - Total period of waveform (in ns)
        /pmw0/duty_cycle    - Active portion of waveform (in ns)
        /pwm0/enable        - '1' to enable pwm, '0' to disable
        /pwm0/polarity      - 'norma' or 'inverted'
    """
    def __init__(self, path_root):
        """Create file paths at the given root and setup watchers."""
        if not os.path.isdir(path_root):
            RuntimeError("'path_root' must be a valid directory.")

        self.root = path_root
        os.makedirs(os.path.join(self.root, "pwm0"))
        with open(os.path.join(self.root, "pwm0", "period"), "w") as f:
            f.write("10000000")
        with open(os.path.join(self.root, "pwm0", "duty_cycle"), "w") as f:
            f.write("1000000")
        with open(os.path.join(self.root, "pwm0", "enable"), "w") as f:
            f.write("0")
        with open(os.path.join(self.root, "pwm0", "polarity"), "w") as f:
            f.write("normal")

    def cleanup(self):
        """Remove any created files and paths"""
        os.remove(os.path.join(self.root, "pwm0", "period"))
        os.remove(os.path.join(self.root, "pwm0", "duty_cycle"))
        os.remove(os.path.join(self.root, "pwm0", "enable"))
        os.remove(os.path.join(self.root, "pwm0", "polarity"))
        os.removedirs(os.path.join(self.root, "pwm0"))

    def on_modified(self, event):
        print(event)


class MockGpioChannel(FileSystemEventHandler):
    """

    Creates the following files:
        /gpio0/direction    - 'in' or 'out', can optionally write 'low' or 'high'
        /gpio0/edge         - One of 'none', 'rising', 'falling', or 'both'
        /gpio0/value        - '0' or '1'
        /gpio0/active_low   - '0', or '1' to invert polarity
    """
    def __init__(self, path_root):
        """Create file paths at the given root and setup watchers."""
        if not os.path.isdir(path_root):
            RuntimeError("'path_root' must be a valid directory.")

        self.root = path_root
        os.makedirs(os.path.join(self.root, "gpio0"))
        with open(os.path.join(self.root, "gpio0", "direction"), "w") as f:
            f.write("in")
        with open(os.path.join(self.root, "gpio0", "edge"), "w") as f:
            f.write("none")
        with open(os.path.join(self.root, "gpio0", "value"), "w") as f:
            f.write("0")
        with open(os.path.join(self.root, "gpio0", "active_low"), "w") as f:
            f.write("0")

    def cleanup(self):
        """Remove any created files and paths"""
        os.remove(os.path.join(self.root, "gpio0", "direction"))
        os.remove(os.path.join(self.root, "gpio0", "edge"))
        os.remove(os.path.join(self.root, "gpio0", "value"))
        os.remove(os.path.join(self.root, "gpio0", "active_low"))
        os.removedirs(os.path.join(self.root, "gpio0"))

    def on_modified(self, event):
        print(event)
