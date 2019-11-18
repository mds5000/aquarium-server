#!/bin/sh

modprobe ads1015
echo "Installed 'ads1015' kernel module."
echo ads1015 0x48 > /sys/bus/i2c/devices/i2c-1/new_device
echo "Added I2C Device ad address 0x48"
