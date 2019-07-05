# aquarium-server
An aquarium controller and monitor application

# Install Instructions
 * pip install virtualenv
 * virtualenv venv -p python3.7
 * source venv/bin/activate
 * pip install -r backend/requirements.txt

# Hardware Configuration

GPIO 4 - Temp Sensor, w1-gpio
GPIO 12 - PWM 0 - Color
GPIO 13 - PWM 1 - Intensity
GPIO 17 - Pump


# Design Documentation

 * Install Scripts
    - Install packages (apt & python)
    - Create system services
    - Compile front-end

 * InfluxDB Server & Telegraph Services
 * Webserver - aio-http
 * Drivers - 

## Drivers
PWM -> rpi use kernel PWM functionality, create a test PWM class that serves as an indicator
GPIO -> use kernel PMW
TEMP -> use kernel 1-wire 


# API
/service(s) -> Get list of service & types
   /module/id/
   /module/id/dashboard {get}
   /module/id/ ... specific module API

# TODO:
 - simplify card result dictionary to single value
 - logging infra
 - START FRONT_END
 - system events

 # Support Tasks
 UDEV Rules for PWM devices
 NTP time sync

# MVP
 - Log Temperature
 - Dosing Pump, static config
 - Kessil profile
 - Log measurements
 - System install / start on reboot
