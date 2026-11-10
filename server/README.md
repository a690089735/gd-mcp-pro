# Godot MCP Pro - Python Server

Python FastMCP implementation for Godot MCP Pro. This replaces the paid Node.js server with a free, open-source Python alternative.

## Architecture

```
AI Assistant (Cline/Claude) ←—stdio/MCP—→ Python FastMCP Server ←—WebSocket:6505—→ Godot Editor Plugin
```

## Requirements

- Python 3.10+
- Godot 4.x with the MCP plugin enabled (from `addons/godot_mcp/`)

## Installation

```bash
cd server
pip install -e .
```

Or install dependencies directly:

```bash
pip install fastmcp websockets
```

## Usage

### 1. Start Godot Editor

Open your Godot project with the MCP plugin enabled:
- **Project → Project Settings → Plugins → Godot MCP Pro → Enable**

### 2. Configure Your AI Client

Add to your MCP client configuration (e.g. `.mcp.json` for Claude Code, or Cline settings):

```json
{
  "mcpServers": {
    "godot-mcp-pro": {
      "command": "python",
      "args": ["-m", "godot_mcp_pro.server"],
      "cwd": "/path/to/server/src",
      "env": {
        "GODOT_MCP_PORT": "6505"
      }
    }
  }
}
```

Or if installed as a package:

```json
{
  "mcpServers": {
    "godot-mcp-pro": {
      "command": "godot-mcp-pro",
      "env": {
        "GODOT_MCP_PORT": "6505"
      }
    }
  }
}
```

### 3. Use It

The server will start a WebSocket server on port 6505 and wait for the Godot editor plugin to connect. Once connected, all 187 MCP tools become available to your AI assistant.

### 4. Optional: Compact Mode

Pass `--compact` to expose **23 umbrella tools** instead of 187 individual ones. Each
umbrella tool takes an `action` string plus a `params` dict, and internally reaches the
exact same 186 Godot commands.

```json
{
  "mcpServers": {
    "godot-mcp-pro": {
      "command": "python",
      "args": ["-m", "godot_mcp_pro.server", "--compact"],
      "cwd": "/path/to/server/src"
    }
  }
}
```

Use it when:
- Your model has a small context window, or degrades with 187 tool definitions
- You want to cut the tool-listing token cost significantly

Trade-off: the AI can only discover parameters from the umbrella tool docstrings, so it
is slightly less reliable at guessing argument names than full mode.

The 23 umbrella tools are: `project`, `scene`, `node`, `script`, `editor`, `input`,
`runtime`, `animation`, `tilemap`, `ui`, `physics`, `scene_3d`, `particles`,
`navigation`, `audio`, `shader`, `resource`, `batch`, `test`, `export`, `diagnostics`,
`headless`, and `batch_execute`.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GODOT_MCP_PORT` | `6505` | WebSocket port for Godot to connect to |
| `GODOT_MCP_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `GODOT_MCP_TOKEN` | *(empty)* | Connection token (if Godot requires one; see `SECURITY.md`) |
| `GODOT_MCP_TOKEN_FILE` | *(empty)* | Path to file containing the connection token |

## CLI Flags

| Flag | Description |
|------|-------------|
| `--compact` | Register 23 umbrella tools instead of 187 individual tools |

## How It Works

1. The Python server starts a **WebSocket server** on the configured port
2. The Godot editor plugin (which acts as a WebSocket **client**) connects to this server
3. When the AI calls an MCP tool, the server:
   - Formats a JSON-RPC 2.0 request
   - Sends it to Godot via WebSocket
   - Waits for the response
   - Returns the result to the AI

## Tool Categories (187 tools total)

| Category | Count | Description |
|----------|-------|-------------|
| Project | 8 | Project metadata, filesystem, search, settings, UID conversion |
| Scene | 10 | Scene CRUD, open/save, play/stop, instancing, exports |
| Node | 17 | Add/delete/move/rename nodes, properties, signals, groups, selection |
| Script | 9 | Script CRUD, editing, attaching, validation, closing/reloading tabs |
| Editor | 14 | Errors, output log, screenshots, editor scripts, 3D camera, plugin reload, unsaved state, save all |
| Input | 7 | Key/mouse/action simulation, sequences, input map |
| Runtime | 19 | Live game inspection, recording/replay, UI probing, movement |
| Animation | 6 | Animation creation, tracks, keyframes |
| AnimationTree | 9 | State machines, transitions, blend trees, blend spaces, IK modifiers |
| TileMap | 6 | Cell operations, fills, tile info |
| Theme | 8 | Theme resources, colors, fonts, styleboxes, Control layout, virtual joystick |
| Profiling | 2 | Game and editor performance monitors |
| Batch | 10 | Bulk operations, cross-scene refactoring, dependency analysis |
| Shader | 6 | Shader creation, editing, materials, parameters |
| Export | 4 | Export presets, info, patch PCK export |
| Resource | 6 | Resource CRUD, previews, autoloads |
| Physics | 6 | Bodies, collisions, layers, raycasts |
| 3D Scene | 7 | Meshes, cameras, lights, environment, GridMap, GridMap inspection, materials |
| Particle | 5 | Particle systems, gradients, presets |
| Navigation | 5 | Regions, agents, baking, layers |
| Audio | 6 | Players, buses, effects, bus layout |
| Testing | 7 | Automated scenarios, assertions, stress tests, game speed |
| Android | 3 | Device management, presets, deployment |
| Analysis | 4 | Scene complexity, signal flow, unused resources, statistics |
| Headless | 3 | Run scenes/scripts in a headless Godot process, get executable path |

> The 187 tools map onto 186 distinct Godot plugin commands plus the pure-Python
> `batch_execute`. Compact mode reaches the same 186 commands through 23 umbrella tools.
>
> Several tools added with plugin v1.17 depend on newer Godot APIs and return a
> "requires Godot X+" error on older editors: `close_script`, `reload_open_scripts`,
> `add_virtual_joystick` (4.7+), `setup_ik_modifier` (4.6+), and the script part of
> `save_all` (4.7+).

## Troubleshooting

### "Not connected to Godot editor"
- Make sure the Godot editor is running with the MCP plugin enabled
- Check that port 6505 is not blocked or in use
- The plugin needs a moment to connect after editor startup

### Connection drops
- The server has auto-reconnect capability
- The Godot plugin will try to reconnect every 3 seconds

### Large responses (screenshots)
- WebSocket buffer is set to 16MB
- Request timeout is 30 seconds by default; long-running tools raise it in both full
  and compact mode (e.g. `move_to`, `watch_signals`, `replay_recording`,
  `bake_navigation_mesh`, headless runs, `export_patch_pck`). Raise the MCP client's
  own timeout too (Cline: `"timeout"` in `cline_mcp_settings.json`), or it may give up
  first.

### `bake_navigation_mesh` appears to hang
- The Godot plugin uses a deprecated baking API that blocks the editor main thread on
  some Godot 4.7 builds. The tool waits up to 120s; if the editor stays frozen you will
  need to restart it.

## License

MIT - Free to use and modify.