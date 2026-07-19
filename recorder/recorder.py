#!/usr/bin/env python3
"""
Message Recorder — crash-safe archive of ALL broker traffic.

Subscribes to every MQTT topic ('#') on the broker and appends each message,
with a timestamp, to a durable append-only log on a persistent volume. If the
whole system shuts down unexpectedly, the archive on disk still holds every
message received up to that moment, so you can inspect / replay it later.

Storage layout (under $RECORD_DIR, default /data/records):
    records/YYYY-MM-DD/<safe_topic>.jsonl   # one JSON object per line

Each line:
    {"ts": "2026-07-19T12:34:56.789Z", "topic": "robots/bot1/telemetry/pose",
     "qos": 1, "retain": false, "payload": <decoded JSON or raw string>}

Environment:
    BROKER_HOST   (default: nanomq)
    BROKER_PORT   (default: 1883)
    RECORD_DIR    (default: /data/records)
    TOPIC_FILTER  (default: #)
    CLIENT_ID     (default: recorder)
"""
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("BROKER_HOST", "nanomq")
BROKER_PORT = int(os.getenv("BROKER_PORT", "1883"))
RECORD_DIR = Path(os.getenv("RECORD_DIR", "/data/records"))
TOPIC_FILTER = os.getenv("TOPIC_FILTER", "#")
CLIENT_ID = os.getenv("CLIENT_ID", "recorder")

_running = True


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _safe_name(topic: str) -> str:
    """Turn an MQTT topic into a filesystem-safe filename."""
    return topic.strip("/").replace("/", "__").replace("+", "_plus_").replace("#", "_hash_") or "root"


def _target_file(topic: str) -> Path:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    directory = RECORD_DIR / day
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{_safe_name(topic)}.jsonl"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[recorder] connected to {BROKER_HOST}:{BROKER_PORT}, subscribing '{TOPIC_FILTER}'", flush=True)
        client.subscribe(TOPIC_FILTER, qos=1)
    else:
        print(f"[recorder] connect failed rc={rc}", flush=True)


def on_message(client, userdata, msg):
    raw = msg.payload.decode("utf-8", errors="replace")
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        payload = raw

    record = {
        "ts": _utc_now(),
        "topic": msg.topic,
        "qos": msg.qos,
        "retain": bool(msg.retain),
        "payload": payload,
    }
    line = json.dumps(record, ensure_ascii=False)
    path = _target_file(msg.topic)
    # Append + flush + fsync so the record is on disk even on a hard crash.
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    print(f"[recorder] {record['ts']} {msg.topic} -> {path.name}", flush=True)


def _shutdown(signum, frame):
    global _running
    print(f"[recorder] signal {signum}, shutting down", flush=True)
    _running = False


def main():
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)
    RECORD_DIR.mkdir(parents=True, exist_ok=True)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id=CLIENT_ID, clean_session=False,
                         protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    while _running:
        try:
            client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
            break
        except OSError as exc:
            print(f"[recorder] broker not ready ({exc}); retry in 3s", flush=True)
            time.sleep(3)

    client.loop_start()
    try:
        while _running:
            time.sleep(1)
    finally:
        client.loop_stop()
        client.disconnect()
        print("[recorder] stopped", flush=True)


if __name__ == "__main__":
    sys.exit(main())
