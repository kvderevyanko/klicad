#!/usr/bin/env bash
set -euo pipefail

project_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
runtime_root="$project_root/.kicad-runtime"

mkdir -p "$runtime_root/config" "$runtime_root/cache" "$runtime_root/data" "$runtime_root/runtime"
chmod 700 "$runtime_root/runtime"

export XDG_CONFIG_HOME="$runtime_root/config"
export XDG_CACHE_HOME="$runtime_root/cache"
export XDG_DATA_HOME="$runtime_root/data"
export XDG_RUNTIME_DIR="$runtime_root/runtime"

exec kicad "${1:-$project_root/hardware/esp32-e220.kicad_pro}"
