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
GPIO -> use kernel gpio
TEMP -> use kernel 1-wire 

## Influx Database

# API
/api
   /<name>
   /<name>/
   /<name>/

# TODO:
- Remove 'calibration' from Hwmon driver
- convert dosing pump to volume instead of duration, with pump calibration
- delete influx telagraph db
- delete aquarium db

- System Monitor
   -- Driver for Si7006
   -- Driver for psutils
      - cpu percentage
      - mem free
      - disk free
      - system uptime
      - app uptime
   -- git hash/app version
   -- Heartbeat LED
   -- Card endpoint

- setup nginx, reverse-proxy


