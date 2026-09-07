# elevenmusic

Generate songs with the [ElevenLabs Music API](https://elevenlabs.io/docs/api-reference/music/create-music) and save them to your workspace.

## Tools

| Tool | Description |
|------|-------------|
| `generate_song` | Generate a song from a text prompt and save the MP3 to workspace |

## Setup

1. **Sign up** for an ElevenLabs account at https://elevenlabs.io/
2. **Get your API key** from the ElevenLabs dashboard
3. **Add it** to your Prax `.env`:

```bash
ELEVENLABS_API_KEY=your_key_here
```

4. **Import the plugin**:

> "Import the elevenmusic plugin from prax-plugins"

**Known gap (2026-09):** as an IMPORTED plugin this currently fails at the key step. `caps.get_approved_secret("ELEVENLABS_API_KEY")` requires the key to be approved for the plugin in Prax's plugin registry, and nothing in Prax approves a secret for an IMPORTED plugin — `PluginRegistry.approve_permission` is called only on the BUILTIN/WORKSPACE load path (`prax/plugins/loader.py`), and there is no agent tool, HTTP route, or UI prompt for it. `generate_song` returns the `PermissionError` message unless `approved_permissions` is added by hand to `prax/plugins/registry.json`.

## Usage

Once installed:

> "Generate a lo-fi hip hop beat for studying"

> "Make a 60 second jazz instrumental"

> "Create a punk rock song about debugging code at 3am"

> "Generate a 2 minute orchestral piece, instrumental only"

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `prompt` | Yes | — | Description of the song (genre, mood, lyrics, instruments, style) |
| `duration_seconds` | No | 30 | Length in seconds (3–600) |
| `instrumental` | No | false | If true, no vocals |

## Permissions

This plugin declares `ELEVENLABS_API_KEY` under `## secrets` in `permissions.md` (the declaration Prax reads for IMPORTED plugins) and also in the legacy `PLUGIN_PERMISSIONS` constant (read only for BUILTIN/WORKSPACE plugins). The key is read through the capabilities gateway's `get_approved_secret()` method — the plugin never reads environment variables directly — and is then placed in the plugin's own request header, so its value does pass through plugin code.

- **BUILTIN/WORKSPACE** plugins: auto-approved at load
- **IMPORTED** plugins: requires the key in the plugin's `approved_permissions` in the registry — see the known gap under Setup

## Requirements

- ElevenLabs API key with music generation access
- Python `requests` library (included with Prax)
