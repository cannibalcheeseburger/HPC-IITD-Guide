#!/bin/sh
# Compatibility alias for the Pragya availability report.
exec "$(dirname "$0")/check_free_nodes.sh" "$@"
