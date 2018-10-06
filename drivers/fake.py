import argparse
import os
import json

import paho.mqtt.client as mqtt

""" MQTT Topics:
/new_device {device_descriptor}
/disconnect {error}      # Will, sent by broker on abnormal termination
/shutdown

/<device_name>/value     # Telemetry, from the device
/<device_name>/update    # Command, from the user
"""

MQTT_HOST = os.environ.get("MQTT_HOSTNAME", "localhost:1883")


class DeviceProvider(object):
    def __init__(self, provider_key, mqtt_host=MQTT_HOST):
        host, port = mqtt_host.split(":")
        self.callbacks = {}
        self.devices = {}
        self.client = mqtt.Client(client_id=provider_key)
        self.client.connect(host, port)

        self.client

    def register_device(self, name, description, units=None, calibration=[], callback=None):
        payload = {
            "name": name,
            "description": description,
            "units": units,
            "calibration": ",".join(calibration)
        }
        self.devices[name] = payload
        self.client.publish("new_device", payload=json.dumps(payload))
        if callback is not None:
            self.subscribe("{}/update".format(name), callback)

    def loop(self, once=True):
        if once:
            self.client.loop()
        else:
            self.client.loop_forever()

    def shutdown(self):
        self.client.disconnect()

    def subscribe(self, topic, callback):
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, callback)

    def publish(self, device, data=dict(), retain=False):
        if device not in self.devices.keys():
            raise KeyError("Unknown device '{}'".format(device))

        payload = json.dumps(data)
        self.client.publish("{}/value".format(device), payload=payload, retain=retain)


if __name__ == "__main__":
    import time
    parser = argparse.ArgumentParser(description="A generic/fake driver for testing.")
    parser.add_argument('--key', default='fake',
                        help="The driver key for this device provider.")
    args = parser.parse_args()

    def led_change(client, userdata, payload):
        print "LED:", userdata, payload.topic, payload.payload

    p = DeviceProvider(args.key)
    p.register_device("led", "a fake LED", callback=led_change)
    state = False
    now = time.time()
    while True:
        p.loop()

        if time.time() > now + 2:
            now = time.time()
            p.publish("led", state)
            state = not state

