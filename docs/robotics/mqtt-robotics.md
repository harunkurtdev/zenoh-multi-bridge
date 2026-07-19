# MQTT-Based Robotics + Persistent Storage

This stack adds an **MQTT-first robotics architecture** with **durable, crash-safe
storage** of all broker traffic on top of the Zenoh multi-protocol bridge.

- **Broker:** NanoMQ (persistent, SQLite-backed) — robots connect here.
- **Bridge:** NanoMQ → `zenoh-mqtt-bridge` → Zenoh mesh → ROS2 (optional).
- **Storage:** a `recorder` service archives **every** message to disk, so after
  an unexpected shutdown you can review exactly what happened.

## Why two layers of persistence?

| Layer | What it keeps | Survives crash? | Use |
|-------|---------------|-----------------|-----|
| NanoMQ SQLite (`nanomq_data`) | retained + QoS 1/2 offline/inflight messages, sessions | Yes | broker keeps working state across restarts |
| Recorder JSONL (`record_data`) | **full timestamped history** of all topics | Yes (fsync per message) | post-mortem / replay / audit |

## Topic architecture

```
robots/<id>/cmd/vel        # -> robot   {"linear","angular"}
robots/<id>/cmd/goal       # -> robot   {"x","y","theta"}
robots/<id>/telemetry/pose      # <- robot  {"x","y","theta"}
robots/<id>/telemetry/battery   # <- robot  {"percent"}
robots/<id>/telemetry/status    # <- robot  {"state"}   (retained + last-will)
robots/<id>/sensor/temperature  # <- robot  {"celsius"}
robots/<id>/sensor/imu          # <- robot  {"ax","ay","wz"}
```

All `robots/**` and `sensor/**` topics are bridged into Zenoh under
`mqtt/demo/robots/**` (see `zenoh-mqtt-bridge/config.json5`), and from there can
reach ROS2 nodes via the ROS2DDS bridge.

## Run it (single machine)

```bash
# Core robotics + persistence stack (NanoMQ, Zenoh, recorder, 2 robots)
docker compose -f docker-compose-robotics.yaml up -d

# Add the ROS2 path (heavy build)
docker compose -f docker-compose-robotics.yaml --profile ros2 up -d

# Watch the fleet from your host
BROKER_HOST=localhost python3 robots/fleet_monitor.py

# Drive a robot
BROKER_HOST=localhost python3 robots/teleop.py vel bot1 0.5 0.2
BROKER_HOST=localhost python3 robots/teleop.py goal bot1 2.0 1.0
BROKER_HOST=localhost python3 robots/teleop.py stop bot1
```

## Run it (distributed r1/r2/r3)

```bash
docker compose -f docker-compose-distributed.yaml up -d
docker compose -f docker-compose-distributed.yaml --profile robots up -d
```

See the header of `docker-compose-distributed.yaml` for splitting the three
routers onto separate PCs.

## Reviewing history after a shutdown

The recorder writes append-only JSONL under the `record_data` volume:

```
records/YYYY-MM-DD/<topic>.jsonl
```

Inspect it with the replay tool (point `--dir` at the mounted volume path):

```bash
# last 50 records
python3 recorder/replay.py --dir /var/lib/docker/volumes/zenoh-multi-bridge_record_data/_data/records --tail 50

# only bot1 pose, within a time window
python3 recorder/replay.py --dir <records-dir> \
  --topic robots/bot1/telemetry/pose \
  --since 2026-07-19T12:00:00 --until 2026-07-19T13:00:00
```

Or copy the archive out of the volume:

```bash
docker cp recorder:/data/records ./records-backup
```

## Notes / next steps

- The NanoMQ config targets **v0.21+** (HOCON). If you pin an older image, align
  the `bridges.mqtt` and `sqlite` sections with that version's schema.
- Authentication is open (`allow_anonymous`) for the demo. Enable NanoMQ auth and
  TLS before any real deployment.
- The robot simulator implements a simple unicycle model; swap it for a real
  robot agent that speaks the same topic scheme and everything downstream
  (bridge, recorder, ROS2) keeps working unchanged.
