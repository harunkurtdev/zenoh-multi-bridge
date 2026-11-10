#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Add a robot to the NanoMQ/Zenoh cluster.
#   1. cluster/robots/<id>/{zenoh.json5,nanomq.conf}  (generated from bot1)
#   2. a replicated "<id>_telemetry" storage on the server
#      (inserted before the @@ROBOT_STORAGES_END@@ marker)
#
# Usage: cluster/scripts/add-robot.sh <robot_id>      e.g.  bot3
# Afterwards restart the server router so it loads the new storage:
#   docker compose -f docker-compose-cluster-server.yaml restart zenoh-server
# -----------------------------------------------------------------------------
set -euo pipefail

ID="${1:-}"
if [[ ! "$ID" =~ ^[a-z0-9_-]+$ ]]; then
  echo "usage: $0 <robot_id>   (lowercase letters, digits, - or _)" >&2
  exit 1
fi

CL="$(cd "$(dirname "$0")/.." && pwd)"
TPL="$CL/robots/bot1"
DIR="$CL/robots/$ID"
SERVER="$CL/server/zenoh.json5"

if [[ -e "$DIR" ]]; then
  echo "$DIR already exists" >&2
  exit 1
fi
if grep -q "^        ${ID}_telemetry:" "$SERVER"; then
  echo "server storage ${ID}_telemetry already exists" >&2
  exit 1
fi

# Unique zenoh id (hex): 2 + 7 hex chars derived from the robot id
ZID="2$(printf '%s' "$ID" | cksum | awk '{printf "%07x", $1 % 268435456}')"

export BLOCK="        ${ID}_telemetry: {
          key_expr: \"robots/${ID}/telemetry/**\",
          strip_prefix: \"robots/${ID}/telemetry\",
          volume: { id: \"fs\", dir: \"${ID}_telemetry\" },
          replication: { interval: 10, sub_intervals: 5, propagation_delay: 250, hot: 6, warm: 30 },
        },"

TMP="$(mktemp)"
# ENVIRON instead of -v: BSD awk (macOS) rejects newlines in -v values
awk '/@@ROBOT_STORAGES_END@@/ { print ENVIRON["BLOCK"] } { print }' "$SERVER" > "$TMP"
grep -q "${ID}_telemetry:" "$TMP" || { rm -f "$TMP"; echo "failed to insert storage (marker missing?)" >&2; exit 1; }
cat "$TMP" > "$SERVER" && rm -f "$TMP"

mkdir -p "$DIR"
for f in zenoh.json5 nanomq.conf; do
  sed -e "s/bot1/${ID}/g" -e "s/id: \"2001\"/id: \"${ZID}\"/" "$TPL/$f" > "$DIR/$f"
done


echo "Created $DIR (zenoh id $ZID)"
echo "Added storage ${ID}_telemetry to $SERVER"
echo
echo "Next:"
echo "  server: docker compose -f docker-compose-cluster-server.yaml restart zenoh-server"
echo "  robot : ROBOT_ID=${ID} SERVER_HOST=<server-ip> docker compose -f docker-compose-cluster-robot.yaml up -d"
