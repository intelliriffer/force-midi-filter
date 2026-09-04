#!/bin/bash
# Run the MIDI filter on Mac
# Usage: ./run_mac.sh [args]
#   e.g., ./run_mac.sh -v  (verbose mode)
#         ./run_mac.sh -l  (list ports)
#         ./run_mac.sh     (run filter with config.ini)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="/Users/atalwar/.local/pipx/venvs/mido/bin/python3"

if [ ! -f "$PYTHON" ]; then
    echo "Error: Python venv not found at $PYTHON"
    echo "Install mido via: pipx install mido"
    exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/midifilter.py" "$@"
