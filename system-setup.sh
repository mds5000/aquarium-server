#!/usr/bin/bash

curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

sudo apt-get update
sudo apt-get install telegraf influxdb


sudo modprobe w1-gpio

#sudo apt-get install pigpio
sudo apt-get install wiringpi

#pip install pigpio
pip install wiringpi


sudo apt-get install mosquitto mosquitto-clients
pip install paho-mqtt
