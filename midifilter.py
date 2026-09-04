#!/usr/bin/env python3
"""
Force MIDI Filter
=================
Filters incoming MIDI input based on a config file and passes filtered
messages to a virtual output port (MidiFilter-Mockba).

Usage:
    python midifilter.py              # Normal mode (read config.ini)
    python midifilter.py -l           # List available MIDI input ports
    python midifilter.py -v           # Verbose logging mode
    python midifilter.py -l -v        # List ports + verbose
"""

import sys
import os
import configparser
import argparse
import time

import mido

# ─── Configuration Variables ───────────────────────────────────────────────
# Set to True to merge all matched ports into one filtered stream.
# Set to False to only use the first matched port.
MERGE_MULTIPLE_PORTS = True

# How often to poll for a MIDI port (in seconds)
POLL_INTERVAL = 5

# Output virtual port name (hardcoded)
OUTPUT_PORT_NAME = "MidiFilter-Mockba"

# Case-insensitive port matching (set False for case-sensitive)
CASE_INSENSITIVE_PORT_MATCH = True

# ─── Message Type Aliases ──────────────────────────────────────────────────
# Maps short user-friendly names to MIDO message types
MESSAGE_TYPE_MAP = {
    "NOTE": "note_on",
    "NOTE_OFF": "note_off",
    "CC": "control_change",
    "PC": "program_change",
    "NOTE_PRESSURE": "note_pressure",
    "AFTERTOUCH": "aftertouch",
    "PITCHBEND": "pitch_bend",
}


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Filter MIDI input based on config rules."
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List available MIDI input ports and exit."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose/debug logging."
    )
    return parser.parse_args()


def list_ports():
    """List all available MIDI input ports."""
    inputs = mido.get_input_names()
    print("\nAvailable MIDI Input Ports:")
    print("-" * 40)
    if not inputs:
        print("  (none found)")
    else:
        for port in sorted(inputs):
            print(f"  - {port}")
    print("-" * 40)
    print()


def find_config_path():
    """Find config.ini in the same directory as this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.ini")
    return config_path


def load_config(config_path, verbose=False):
    """
    Load and parse the config.ini file.
    Returns a dict with 'midi_port' (str) and 'channels' (dict).
    """
    config = configparser.ConfigParser(interpolation=None)
    config.read(config_path)

    result = {"midi_port": None, "channels": {}}

    # Read MIDI_PORT from DEFAULT section
    if config.has_option("DEFAULT", "MIDI_PORT"):
        result["midi_port"] = config.get("DEFAULT", "MIDI_PORT").strip()
    else:
        print("Error: MIDI_PORT not defined in config.ini")
        sys.exit(1)

    # Read channel rules from all sections
    for section in config.sections():
        # Sections should be like [CH-1], [CH-2], etc.
        if section.startswith("CH-"):
            ch_num_str = section[3:]  # Extract number after "CH-"
            try:
                ch_num = int(ch_num_str)
            except ValueError:
                if verbose:
                    print(f"Warning: Skipping invalid channel section [{section}]")
                continue

            if ch_num < 1 or ch_num > 16:
                if verbose:
                    print(f"Warning: Channel {ch_num} out of range (1-16), skipping")
                continue

            # Read the value (message types)
            value = config.get(section, "RULE").strip().upper()

            if value == "BLOCK":
                result["channels"][ch_num] = {"type": "block"}
            elif value == "ALL":
                result["channels"][ch_num] = {"type": "all"}
            else:
                # Parse comma-separated message types
                msg_types = [t.strip().upper() for t in value.split(",")]
                # Validate message types
                valid_types = set(MESSAGE_TYPE_MAP.keys())
                for mt in msg_types:
                    if mt not in valid_types:
                        print(f"Warning: Unknown message type '{mt}' for CH-{ch_num}")
                result["channels"][ch_num] = {"type": "allow", "messages": msg_types}

    return result


def match_midi_ports(port_name, verbose=False):
    """
    Find all MIDI input ports matching the given name (wildcard).
    Returns a list of matching port names.
    """
    all_inputs = mido.get_input_names()
    matched = []

    for port in all_inputs:
        compare_port = port
        compare_name = port_name

        if CASE_INSENSITIVE_PORT_MATCH:
            compare_port = compare_port.lower()
            compare_name = compare_name.lower()

        if compare_name in compare_port:
            matched.append(port)
            if verbose:
                print(f"  [MATCH] '{port_name}' matched '{port}'")

    return matched


def wait_for_ports(port_names, verbose=False):
    """
    Wait until all specified ports are available.
    Polls every POLL_INTERVAL seconds.
    """
    while True:
        available = mido.get_input_names()
        missing = []

        for name in port_names:
            found = False
            for port in available:
                compare_port = port
                compare_name = name
                if CASE_INSENSITIVE_PORT_MATCH:
                    compare_port = compare_port.lower()
                    compare_name = name.lower()
                if compare_name in compare_port:
                    found = True
                    break
            if not found:
                missing.append(name)

        if not missing:
            if verbose:
                print(f"All ports available: {port_names}")
            return port_names

        if verbose:
            print(f"Waiting for ports: {missing}")
        else:
            print(f"Waiting for MIDI ports: {', '.join(missing)}...")

        time.sleep(POLL_INTERVAL)


def is_message_allowed(msg, channel_rules):
    """
    Check if a MIDI message should be allowed through based on channel rules.
    Returns True if allowed, False if blocked.
    """
    ch = msg.channel if hasattr(msg, 'channel') and msg.channel is not None else 0
    msg_type = msg.type

    # If channel has a rule
    if ch in channel_rules:
        rule = channel_rules[ch]

        if rule["type"] == "block":
            return False

        if rule["type"] == "all":
            return True

        if rule["type"] == "allow":
            # Map MIDO message type to our alias
            for alias, mido_type in MESSAGE_TYPE_MAP.items():
                if mido_type == msg_type:
                    if alias in rule["messages"]:
                        return True
                    else:
                        return False
            # If message type not in our map, block it
            return False

    # No rule for this channel → BLOCKED
    return False


def create_output_port():
    """Create or get the virtual output port."""
    # Check if output port already exists
    outputs = mido.get_output_names()
    for port in outputs:
        if OUTPUT_PORT_NAME in port:
            return mido.open_output(port)

    # Create new virtual port
    try:
        out_port = mido.open_output(OUTPUT_PORT_NAME, virtual=True)
        print(f"Created output port: {OUTPUT_PORT_NAME}")
        return out_port
    except OSError as e:
        print(f"Error: Could not create output port '{OUTPUT_PORT_NAME}': {e}")
        sys.exit(1)


def run_filter(config, verbose=False):
    """Main filter loop."""
    port_name = config["midi_port"]
    channels = config["channels"]

    if verbose:
        print(f"MIDI_PORT pattern: '{port_name}'")
        print(f"Channel rules: {channels}")

    # Find matching ports
    matched_ports = match_midi_ports(port_name, verbose)

    if not matched_ports:
        print(f"No ports matching '{port_name}' found. Waiting...")

    # Wait for ports to become available
    available_ports = wait_for_ports(matched_ports, verbose)

    if not MERGE_MULTIPLE_PORTS and len(available_ports) > 1:
        available_ports = [available_ports[0]]
        if verbose:
            print(f"Using only first port: {available_ports[0]}")

    # Create output port
    out_port = create_output_port()

    print(f"Filtering: {', '.join(available_ports)} → {OUTPUT_PORT_NAME}")
    print("Press Ctrl+C to stop.\n")

    # Open input ports
    in_ports = []
    for port_name in available_ports:
        try:
            in_port = mido.open_input(port_name)
            in_ports.append(in_port)
            if verbose:
                print(f"Opened input: {port_name}")
        except OSError as e:
            print(f"Warning: Could not open port '{port_name}': {e}")

    # Callback for handling incoming messages
    def on_message(msg, port_name=""):
        if is_message_allowed(msg, channels):
            out_port.send(msg)
            if verbose:
                print(f"  PASS: [{port_name}] {msg}")
        else:
            if verbose:
                print(f"  DROP: [{port_name}] {msg}")

    # Set up callbacks
    for in_port in in_ports:
        in_port.callback = lambda msg, p=in_port.name: on_message(msg, p)

    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping filter...")
    finally:
        for in_port in in_ports:
            in_port.close()
        out_port.close()
        print("Done.")


def main():
    args = parse_args()
    verbose = args.verbose

    if args.list:
        list_ports()
        return

    # Load config
    config_path = find_config_path()
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    if verbose:
        print(f"Loading config from: {config_path}\n")

    config = load_config(config_path, verbose)

    # Run the filter
    run_filter(config, verbose)


if __name__ == "__main__":
    main()
