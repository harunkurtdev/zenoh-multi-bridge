#!/usr/bin/env python3
"""
Fleet Monitor — live view of all robots' telemetry and sensors.

Subscribes to robots/+/telemetry/# and robots/+/sensor/# and prints a
running feed. Useful to watch the whole fleet from your host machine.

Environment:
  BROKER_HOST (default: localhost)
  BROKER_PORT (default: 1883)
"""
import json
import os

import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("BROKER_HOST", "localhost")
BROKER_PORT = int(os.getenv("BROKER_PORT", "1883"))


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"[monitor] connected rc={rc}", flush=True)
    client.subscribe("robots/+/telemetry/#", qos=1)
    client.subscribe("robots/+/sensor/#", qos=0)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, ValueError):
        payload = msg.payload.decode("utf-8", errors="replace")
    print(f"{msg.topic:45s} {payload}", flush=True)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id="fleet-monitor", protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()


if __name__ == "__main__":
    main()
