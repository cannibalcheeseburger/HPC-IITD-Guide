#!/bin/sh
# Padum availability report; run on a Padum login node.
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
exec python3 "$script_dir/util_pbs.py" --cluster padum "$@"
