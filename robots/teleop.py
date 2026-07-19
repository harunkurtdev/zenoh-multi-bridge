#!/usr/bin/env python3
"""
Teleop — send commands to a robot over MQTT.

Usage:
  python3 teleop.py vel <robot_id> <linear> <angular>
  python3 teleop.py goal <robot_id> <x> <y> [theta]
  python3 teleop.py stop <robot_id>

Examples:
  python3 teleop.py vel bot1 0.5 0.2
  python3 teleop.py goal bot1 2.0 1.0
  python3 teleop.py stop bot1

Environment:
  BROKER_HOST (default: localhost)   # host access via the published 1883 port
  BROKER_PORT (default: 1883)
"""
import json
import os
import sys

import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("BROKER_HOST", "localhost")
BROKER_PORT = int(os.getenv("BROKER_PORT", "1883"))


def publish(topic: str, payload: dict):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311)
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=10)
    client.loop_start()
    info = client.publish(topic, json.dumps(payload), qos=1)
    info.wait_for_publish()
    client.loop_stop()
    client.disconnect()
    print(f"-> {topic}: {payload}")


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1

    action, robot_id = argv[1], argv[2]
    base = f"robots/{robot_id}"

    if action == "vel" and len(argv) >= 5:
        publish(f"{base}/cmd/vel",
                {"linear": float(argv[3]), "angular": float(argv[4])})
    elif action == "goal" and len(argv) >= 5:
        payload = {"x": float(argv[3]), "y": float(argv[4])}
        if len(argv) >= 6:
            payload["theta"] = float(argv[5])
        publish(f"{base}/cmd/goal", payload)
    elif action == "stop":
        publish(f"{base}/cmd/vel", {"linear": 0.0, "angular": 0.0})
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
