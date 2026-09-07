# radio

Stream a directory of audio files as an internet radio station. Listeners connect with any media player (VLC, browsers, mpv) and hear the same continuous broadcast.

## Tools

| Tool | Description |
|------|-------------|
| `start_radio` | Start streaming audio files from a directory |
| `stop_radio` | Stop the station and disconnect all listeners |
| `radio_status` | Check what's playing, listener count, and stream URL |
| `radio_skip` | Skip to the next track |
| `radio_queue` | Show upcoming tracks in the playlist |

## Setup

No API keys required. Just add audio files to a directory.

### Supported formats

MP3, OGG, WAV, FLAC, AAC, M4A

### Optional: public access via ngrok

Install [ngrok](https://ngrok.com/download) to expose the stream publicly:

```bash
# macOS
brew install ngrok

# or download from https://ngrok.com/download
```

Then use `expose_ngrok=True` when starting the station.

**Known gap (2026-09):** this does not work with the shipped `permissions.md`. `_try_ngrok()` in `plugin.py` launches ngrok via `caps.run_command(["sh", "-c", "nohup ngrok http <port> …"])` and `stop()` cleans up with `caps.run_command(["pkill", "-f", "ngrok http"])`, but `## allowed_commands` lists only `ngrok`, `ffprobe`, `which`. Prax rejects any `run_command` whose argv[0] is not on that list (`prax/plugins/capabilities.py`, `run_command`); `_try_ngrok()` catches the error and returns `None`, so the tool reports "ngrok not available" even when ngrok is installed. Note also that in Docker-compose deployments of Prax (`RUNNING_IN_DOCKER=true`), `caps.run_command` executes inside the sandbox container (`prax/utils/shell.py`, `run_command`), not on the machine where this plugin's HTTP server listens.

## Usage

> "Start a radio station from my music folder"

> "Play all the songs in my workspace as a radio stream"

> "Start Prax Radio with shuffle on and expose it via ngrok"

> "What's playing on the radio?"

> "Skip this track"

> "Stop the radio"

### Parameters (`start_radio`)

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `music_directory` | No | `music/` under the plugin's scoped directory | Path to audio files (scans subdirectories). The default comes from `caps.workspace_path("music")`; for an imported plugin that is inside the plugin's `plugin_data/…/` directory in the workspace, not the workspace root. |
| `shuffle` | No | true | Randomize track order |
| `station_name` | No | "Prax Radio" | Name shown in player metadata |
| `expose_ngrok` | No | false | Create a public ngrok tunnel |
| `port` | No | auto | Specific port number (0 = auto) |

### Listening

Connect with any media player:

```bash
# VLC
vlc http://localhost:PORT/stream

# mpv
mpv http://localhost:PORT/stream

# curl (save to file)
curl http://localhost:PORT/stream -o radio.mp3

# Browser
# Just open http://localhost:PORT/stream
```

### HTTP endpoints

| Endpoint | Description |
|----------|-------------|
| `/stream` | Audio stream (MP3 over HTTP, SHOUTcast-compatible) |
| `/status` | JSON status (current track, listeners, uptime) |
| `/playlist` | JSON playlist with current position |

## How it works

1. Scans the music directory recursively for audio files
2. Binds a stdlib `http.server.HTTPServer` on `0.0.0.0` (all interfaces) on the requested port (0 = OS-assigned) and serves it from a background thread. There is no authentication: anyone who can reach the port can listen and read `/status` and `/playlist`. For an imported plugin this server runs in Prax's plugin host subprocess on the machine running Prax (not in the sandbox).
3. A broadcast thread reads audio files sequentially (or shuffled) and pushes chunks to all connected listeners
4. Listeners receive the same stream — everyone hears the same thing at the same time (like real radio)
5. When the playlist ends, it reshuffles and loops
6. Optionally creates an ngrok tunnel for public access (see the known gap under Setup — not functional with the shipped `permissions.md`)

## Requirements

- Python standard library only (no additional packages)
- Audio files in a directory
- Optional: ngrok for public access (see the known gap under Setup)
