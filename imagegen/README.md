# imagegen

Generate and edit images with the [OpenAI Images API](https://platform.openai.com/docs/api-reference/images) (`gpt-image-1`) and save them as PNG to the plugin's workspace directory.

## Tools

| Tool | Description |
|------|-------------|
| `generate_image` | Generate an image from a text prompt (`POST /v1/images/generations`) |
| `edit_image` | Edit an existing image in the workspace from a text prompt (`POST /v1/images/edits`, multipart) |

## Setup

1. Set `OPENAI_KEY` in Prax's environment (the plugin reads it as an approved secret; it never reads environment variables or settings directly).
2. Import the plugin:

> "Import the imagegen plugin from prax-plugins"

**Known gap (2026-09):** as an IMPORTED plugin this currently fails at the key step. `caps.get_approved_secret("OPENAI_KEY")` requires the key to be approved for the plugin in Prax's plugin registry, and nothing in Prax approves a secret for an IMPORTED plugin — `PluginRegistry.approve_permission` is called only on the BUILTIN/WORKSPACE load path (`prax/plugins/loader.py`), and there is no agent tool, HTTP route, or UI prompt for it. Both tools return the `PermissionError` message unless `approved_permissions` is added by hand to `prax/plugins/registry.json`.

## Usage

> "Generate an image of a lighthouse at dusk, photorealistic"

> "Edit sunset_123.png: add a red boat in the foreground"

### Parameters (`generate_image`)

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `prompt` | Yes | — | Description of the image |
| `size` | No | `1024x1024` | One of `1024x1024`, `1536x1024`, `1024x1536`, `auto`; any other value silently falls back to `1024x1024` |
| `quality` | No | `auto` | One of `low`, `medium`, `high`, `auto`; other values fall back to `auto` |
| `style` | No | `auto` | `natural`, `vivid`, or `auto`; sent to the API only when not `auto` |

### Parameters (`edit_image`)

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `image_path` | Yes | — | Source image. Read via `caps.read_file()` / `caps.workspace_path()`, so for an imported plugin it must be inside the plugin's scoped `plugin_data/…/` directory |
| `prompt` | Yes | — | The edit to make |
| `size` | No | `1024x1024` | Same options and fallback as `generate_image` |

### Output

PNG bytes are saved with `caps.save_file()` as `<prompt-slug>_<unix-timestamp>.png` (edits: `<prompt-slug>_edited_<unix-timestamp>.png`) in the plugin's scoped directory; the tool returns the saved path, size in KB, and the prompt. Every request asks for `model: gpt-image-1` and a single image (`n=1`).

## Permissions

`permissions.md` declares:

```markdown
## capabilities
- http
- filesystem

## secrets
- OPENAI_KEY: Authenticate with the OpenAI Images API (gpt-image-1) for generation and editing
```

`plugin.py` also carries the legacy `PLUGIN_PERMISSIONS` constant for the same key (read only for BUILTIN/WORKSPACE plugins). The key's value is obtained from `caps.get_approved_secret("OPENAI_KEY")` and placed in the `Authorization: Bearer …` header of the plugin's own `caps.http_post()` calls to `api.openai.com` — so, unlike the LLM/TTS gateway paths, the key does pass through plugin code. No shell commands are declared or used.

## Requirements

- An OpenAI API key with Images API access
- Nothing beyond Prax's own dependencies (HTTP goes through `caps.http_post()`)

## Tests

```bash
uv run pytest tests/test_imagegen.py -q      # mocked caps, no API key
```
