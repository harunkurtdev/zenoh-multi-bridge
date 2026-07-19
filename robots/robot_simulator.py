#!/usr/bin/env python3
"""
Robot Simulator — a virtual MQTT robot for the robotics stack.

Implements the command + telemetry + sensor loop:
  * Subscribes to command topics and drives simple 2D kinematics.
  * Publishes telemetry (pose, battery, status) and sensor data periodically.

Topic scheme (all under the broker root, bridged into Zenoh as mqtt/demo/...):
  IN  robots/<id>/cmd/vel     {"linear": 0.5, "angular": 0.1}
  IN  robots/<id>/cmd/goal    {"x": 2.0, "y": 1.0, "theta": 0.0}
  OUT robots/<id>/telemetry/pose      {"x","y","theta"}
  OUT robots/<id>/telemetry/battery   {"percent"}
  OUT robots/<id>/telemetry/status    {"state","ts"}          (retained)
  OUT robots/<id>/sensor/temperature  {"celsius"}
  OUT robots/<id>/sensor/imu          {"ax","ay","wz"}

Environment:
  ROBOT_ID     (default: bot1)
  BROKER_HOST  (default: nanomq)
  BROKER_PORT  (default: 1883)
  RATE_HZ      (default: 5)   telemetry publish rate
"""
import json
import math
import os
import signal
import time

import paho.mqtt.client as mqtt

ROBOT_ID = os.getenv("ROBOT_ID", "bot1")
BROKER_HOST = os.getenv("BROKER_HOST", "nanomq")
BROKER_PORT = int(os.getenv("BROKER_PORT", "1883"))
RATE_HZ = float(os.getenv("RATE_HZ", "5"))

BASE = f"robots/{ROBOT_ID}"
_running = True

# --- Robot state -------------------------------------------------------------
state = {"x": 0.0, "y": 0.0, "theta": 0.0}
cmd = {"linear": 0.0, "angular": 0.0}
battery = 100.0


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"[{ROBOT_ID}] connected rc={rc}", flush=True)
    client.subscribe(f"{BASE}/cmd/vel", qos=1)
    client.subscribe(f"{BASE}/cmd/goal", qos=1)
    client.publish(f"{BASE}/telemetry/status",
                   json.dumps({"state": "online", "ts": time.time()}),
                   qos=1, retain=True)


def on_message(client, userdata, msg):
    global cmd
    try:
        data = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, ValueError):
        print(f"[{ROBOT_ID}] bad command on {msg.topic}", flush=True)
        return

    if msg.topic.endswith("/cmd/vel"):
        cmd["linear"] = float(data.get("linear", 0.0))
        cmd["angular"] = float(data.get("angular", 0.0))
        print(f"[{ROBOT_ID}] cmd/vel linear={cmd['linear']} angular={cmd['angular']}", flush=True)
    elif msg.topic.endswith("/cmd/goal"):
        # Naive goal-seeking: point toward the goal at fixed speed.
        gx, gy = float(data.get("x", 0.0)), float(data.get("y", 0.0))
        dx, dy = gx - state["x"], gy - state["y"]
        target = math.atan2(dy, dx)
        cmd["angular"] = max(-1.0, min(1.0, target - state["theta"]))
        cmd["linear"] = 0.5 if math.hypot(dx, dy) > 0.1 else 0.0
        print(f"[{ROBOT_ID}] cmd/goal ({gx},{gy})", flush=True)


def _shutdown(signum, frame):
    global _running
    _running = False


def main():
    global battery
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id=f"robot-{ROBOT_ID}", protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message
    # Last-will so the fleet sees a crash immediately.
    client.will_set(f"{BASE}/telemetry/status",
                    json.dumps({"state": "offline", "ts": time.time()}),
                    qos=1, retain=True)
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    while _running:
        try:
            client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
            break
        except OSError as exc:
            print(f"[{ROBOT_ID}] broker not ready ({exc}); retry", flush=True)
            time.sleep(3)

    client.loop_start()
    dt = 1.0 / RATE_HZ
    tick = 0
    try:
        while _running:
            # Integrate simple unicycle kinematics.
            state["theta"] += cmd["angular"] * dt
            state["x"] += cmd["linear"] * math.cos(state["theta"]) * dt
            state["y"] += cmd["linear"] * math.sin(state["theta"]) * dt
            battery = max(0.0, battery - 0.01)

            client.publish(f"{BASE}/telemetry/pose",
                           json.dumps({k: round(state[k], 4) for k in state}), qos=1)
            client.publish(f"{BASE}/sensor/imu",
                           json.dumps({"ax": round(cmd["linear"], 3),
                                       "ay": 0.0,
                                       "wz": round(cmd["angular"], 3)}), qos=0)

            if tick % RATE_HZ == 0:  # ~1 Hz for slow-changing values
                client.publish(f"{BASE}/telemetry/battery",
                               json.dumps({"percent": round(battery, 2)}), qos=1)
                client.publish(f"{BASE}/sensor/temperature",
                               json.dumps({"celsius": round(25 + 5 * math.sin(tick / 20), 2)}), qos=0)

            tick += 1
            time.sleep(dt)
    finally:
        client.publish(f"{BASE}/telemetry/status",
                       json.dumps({"state": "offline", "ts": time.time()}),
                       qos=1, retain=True)
        client.loop_stop()
        client.disconnect()
        print(f"[{ROBOT_ID}] stopped", flush=True)


if __name__ == "__main__":
    main()
