#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Put the zenoh 1.0.0 plugin libraries into cluster/plugins/lib, which every
# zenoh container mounts at /root/.zenoh/lib.
#
# Required (exact zenohd 1.0.0 ABI, x86_64 linux):
#   libzenoh_plugin_mqtt.so  libzenoh_plugin_storage_manager.so  libzenoh_backend_fs.so
# Optional: libzenoh_plugin_rest.so (rest is also built into zenohd)
#
# Usage:
#   cluster/scripts/fetch-zenoh-plugins.sh [SOURCE_DIR]
#   SOURCE_DIR defaults to ../zenoh-mqtt-nanomq/zenoh/lib (sibling checkout)
# Nothing is pulled with docker; files are only copied.
# -----------------------------------------------------------------------------
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="${1:-$ROOT/../zenoh-mqtt-nanomq/zenoh/lib}"
DST="$ROOT/cluster/plugins/lib"
REQUIRED=(libzenoh_plugin_mqtt.so libzenoh_plugin_storage_manager.so libzenoh_backend_fs.so)
OPTIONAL=(libzenoh_plugin_rest.so libzenoh_backend_rocksdb.so)

if [[ ! -d "$SRC" ]]; then
  echo "Source directory not found: $SRC" >&2
  echo "Pass the directory containing the zenoh 1.0.0 plugin .so files as the first argument." >&2
  exit 1
fi

mkdir -p "$DST"
for lib in "${REQUIRED[@]}"; do
  if [[ ! -f "$SRC/$lib" ]]; then
    echo "Missing required plugin: $SRC/$lib" >&2
    exit 1
  fi
  cp -f "$SRC/$lib" "$DST/"
  echo "copied  $lib"
done
for lib in "${OPTIONAL[@]}"; do
  if [[ -f "$SRC/$lib" ]]; then cp -f "$SRC/$lib" "$DST/"; echo "copied  $lib (optional)"; fi
done
echo "Plugins ready in $DST"
