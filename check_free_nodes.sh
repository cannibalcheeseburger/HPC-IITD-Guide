#!/bin/sh
# Shared PBS report; HPC_CLUSTER or --cluster can override auto-detection.
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
exec python3 "$script_dir/util_pbs.py" "$@"
