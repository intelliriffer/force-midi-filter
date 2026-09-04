#!/bin/bash
# Run tests for the MIDI filter on Mac
# Usage: ./test_mac.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="/Users/atalwar/.local/pipx/venvs/mido/bin/python3"

if [ ! -f "$PYTHON" ]; then
    echo "Error: Python venv not found at $PYTHON"
    echo "Install mido via: pipx install mido"
    exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/test.py"
