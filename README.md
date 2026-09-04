# Force MIDI Filter

A Python script that filters incoming MIDI input based on channel-specific rules and passes filtered messages to a virtual output port. Designed for use with the Akai Force and macOS.

## Features

- **MIDI port wildcard matching** — Match ports by partial name (case-insensitive by default)
- **Channel-based filtering** — Block, allow all, or allow specific message types per channel
- **Virtual output port** — Creates `MidiFilter-Mockba` as the filtered output
- **Auto-reconnect** — Polls for missing ports every 5 seconds
- **Configurable** — Easy-to-edit INI config file with comments

## Installation

### On the Akai Force (Mockba mod)

The Mockba mod ships with Python preinstalled — **no setup needed**. Just copy the files (`midifilter.py`, `config.ini`) to the Force and run the script. If `mido` is not already present in the mod's Python, install it once:

```bash
pip install mido
```

### On macOS / Linux

1. Install Python 3.8+ (if not already installed)
2. Install the MIDO library:

```bash
pip install mido
```

> `mido` pulls in `python-rtmidi` automatically. On some systems you may also need the portaudio/rtmidi system library (e.g. `brew install portaudio` on macOS or `sudo apt install libportaudio2` on Linux) if the `rtmidi` build fails.

No other dependencies required.

## Usage

### List available MIDI input ports

```bash
python midifilter.py -l
```

### Run the filter

```bash
python midifilter.py
```

### Verbose mode (debug logging)

```bash
python midifilter.py -v
```

## Configuration

Edit `config.ini` in the same directory as `midifilter.py`.

### MIDI Port

```ini
MIDI_PORT=Force
```

Uses wildcard matching — any port containing "Force" will be opened.

### Channel Rules

```ini
[CH-1]
RULE=ALL

[CH-2]
RULE=CC,PC

[CH-3]
RULE=NOTE,CC,AFTERTOUCH,PITCHBEND

[CH-4]
RULE=BLOCK
```

#### Rule Types

| Rule | Description |
|------|-------------|
| `ALL` | Pass all messages on this channel |
| `BLOCK` | Block all messages on this channel |
| `CC,PC,NOTE,...` | Only pass the specified message types |

#### Message Type Aliases

| Alias | Description |
|-------|-------------|
| `NOTE` | Note On / Note Off |
| `CC` | Control Change |
| `PC` | Program Change |
| `NOTE_PRESSURE` | Note Pressure (per-note aftertouch) |
| `AFTERTOUCH` | Channel Aftertouch |
| `PITCHBEND` | Pitch Bend |

Any channel not listed in the config is automatically **BLOCKED**.

## Script Variables

These can be edited in `midifilter.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MERGE_MULTIPLE_PORTS` | `True` | Merge all matched ports into one stream |
| `POLL_INTERVAL` | `5` | Seconds between port availability checks |
| `OUTPUT_PORT_NAME` | `MidiFilter-Mockba` | Name of the virtual output port |
| `CASE_INSENSITIVE_PORT_MATCH` | `True` | Case-insensitive port name matching |

## Testing

Run the test suite:

```bash
python test.py
```

## Files

| File | Description |
|------|-------------|
| `midifilter.py` | Main MIDI filter script |
| `config.ini` | Configuration file |
| `test.py` | Unit tests |
| `README.md` | This file |
| `requirements.md` | Project requirements |

## License

MIT
