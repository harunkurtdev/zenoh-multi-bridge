#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Show which node physically stores which topics (fs backend directories).
# Disk is checked instead of REST because a REST query on the server is routed
# to the robot storages too, so it can't tell you where the data actually lives.
#
# Usage: cluster/scripts/check-storage.sh [robot_id ...]     (default: bot1 bot2)
# Single host: works out of the box. Distributed: run it on each machine; dirs
# that don't exist on that machine are shown as "-".
# -----------------------------------------------------------------------------
set -uo pipefail

DATA="$(cd "$(dirname "$0")/.." && pwd)/data"
ROBOTS=("$@")
[[ ${#ROBOTS[@]} -eq 0 ]] && ROBOTS=(bot1 bot2)

keys() {  # number of stored keys (files) in a storage dir
  [[ -d "$1" ]] || { echo "-"; return; }
  find "$1" -type f ! -name '.*' ! -path '*/.*' | wc -l | tr -d ' '
}

printf "%-8s %-26s %-12s %-12s\n" ROBOT TOPIC "ON ROBOT" "ON SERVER"
for id in "${ROBOTS[@]}"; do
  for cat in telemetry sensor; do
    printf "%-8s %-26s %-12s %-12s\n" "$id" "robots/$id/$cat/#" \
      "$(keys "$DATA/zenoh-$id/${id}_$cat")" "$(keys "$DATA/zenoh-server/${id}_$cat")"
  done
done
printf "%-8s %-26s %-12s %-12s\n" "-" "fleet/#" "-" "$(keys "$DATA/zenoh-server/fleet")"
echo
echo "Expected: telemetry on ROBOT + SERVER, sensor on ROBOT only, fleet on SERVER only."
