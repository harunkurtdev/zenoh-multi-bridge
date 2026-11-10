#!/bin/sh
# -----------------------------------------------------------------------------
# Minimal robot simulator (POSIX sh + nanomq_cli, runs inside the NanoMQ image).
#   publishes robots/$ROBOT_ID/telemetry/{status,pose,battery}  (robot + server)
#             robots/$ROBOT_ID/sensor/{temperature,imu}         (robot only)
#   prints    robots/$ROBOT_ID/cmd/#                            (from the server)
# Env: ROBOT_ID (bot1), BROKER_HOST (localhost), BROKER_PORT (1883), PERIOD (1 s)
# -----------------------------------------------------------------------------
ROBOT_ID="${ROBOT_ID:-bot1}"
HOST="${BROKER_HOST:-localhost}"
PORT="${BROKER_PORT:-1883}"
PERIOD="${PERIOD:-1}"
BASE="robots/$ROBOT_ID"

pub() {  # pub <topic> <json> <qos>
  nanomq_cli pub -h "$HOST" -p "$PORT" -t "$1" -m "$2" -q "$3" >/dev/null 2>&1 \
    || echo "[$ROBOT_ID] publish failed: $1"
}

until nanomq_cli pub -h "$HOST" -p "$PORT" -t "$BASE/telemetry/status" \
        -m "{\"state\":\"online\",\"ts\":$(date +%s)}" -q 1 >/dev/null 2>&1; do
  echo "[$ROBOT_ID] waiting for broker $HOST:$PORT"; sleep 3
done
echo "[$ROBOT_ID] online -> $HOST:$PORT"

# commands coming from the server cluster
nanomq_cli sub -h "$HOST" -p "$PORT" -t "$BASE/cmd/#" -q 1 &

trap 'pub "$BASE/telemetry/status" "{\"state\":\"offline\",\"ts\":$(date +%s)}" 1; exit 0' INT TERM

tick=0
battery=10000                       # hundredths of a percent
while :; do
  tick=$((tick + 1))
  battery=$((battery > 0 ? battery - 1 : 0))
  x=$((tick % 100)); y=$(((tick * 3) % 100))
  pub "$BASE/telemetry/pose"    "{\"x\":$x,\"y\":$y,\"theta\":0}" 1
  pub "$BASE/telemetry/battery" "{\"percent\":$((battery / 100)).$((battery % 100))}" 1
  pub "$BASE/sensor/imu"        "{\"ax\":0,\"ay\":0,\"wz\":$((tick % 7))}" 0
  pub "$BASE/sensor/temperature" "{\"celsius\":$((25 + tick % 5))}" 0
  sleep "$PERIOD" & wait $!
done
