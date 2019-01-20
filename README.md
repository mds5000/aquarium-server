# aquarium-server
An aquarium controller and monitor application


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


A: Temperature logger
 - full query API
 - hardcoded sensor logged to DB
 - graph widget UI
B: GPIO controller
 - hardcoded GPIO devices
 - change events logged to DB
C: PWM controller
 - hardcoded devices
 - change events logged to DB
D: PWM profile
 - profile API
 - time sync
 - profile with interpolation

x mock devices for testing
x temp device driver/task
x push to influxdb
x front-end API
x test database 
- configuration database
- config database test
- temp sensor test cases

- deploy temp sensor to pi
- implement GPIO driver
- front-end API
- add logging


# Database
- devices (pwm, gpio, temp, ... analog_in, )
- Modules (group of devices matching template)
   - kessil
   - dosing
   - alarm

# API
/device {get, post, /id/}
   /device/id/ {get, post, delete}
   /device/id/value {get, post}
/module {get, post, /id/}
   /module/id/ {get, post, delete}
   /module/id/dashboard {get}
   /module/id/ ... specific module API