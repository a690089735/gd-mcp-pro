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

The server will start a WebSocket server on port 6505 and wait for the Godot editor plugin to connect. Once connected, all 175 MCP tools become available to your AI assistant.

### 4. Optional: Compact Mode

Pass `--compact` to expose **22 umbrella tools** instead of 175 individual ones. Each
umbrella tool takes an `action` string plus a `params` dict, and internally reaches the
exact same 174 Godot commands.

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
- Your model has a small context window, or degrades with 175 tool definitions
- You want to cut the tool-listing token cost significantly

Trade-off: the AI can only discover parameters from the umbrella tool docstrings, so it
is slightly less reliable at guessing argument names than full mode.

The 22 umbrella tools are: `project`, `scene`, `node`, `script`, `editor`, `input`,
`runtime`, `animation`, `tilemap`, `ui`, `physics`, `scene_3d`, `particles`,
`navigation`, `audio`, `shader`, `resource`, `batch`, `test`, `export`, `diagnostics`,
and `batch_execute`.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GODOT_MCP_PORT` | `6505` | WebSocket port for Godot to connect to |
| `GODOT_MCP_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## CLI Flags

| Flag | Description |
|------|-------------|
| `--compact` | Register 22 umbrella tools instead of 175 individual tools |

## How It Works

1. The Python server starts a **WebSocket server** on the configured port
2. The Godot editor plugin (which acts as a WebSocket **client**) connects to this server
3. When the AI calls an MCP tool, the server:
   - Formats a JSON-RPC 2.0 request
   - Sends it to Godot via WebSocket
   - Waits for the response
   - Returns the result to the AI

## Tool Categories (175 tools total)

| Category | Count | Description |
|----------|-------|-------------|
| Project | 8 | Project metadata, filesystem, search, settings, UID conversion |
| Scene | 10 | Scene CRUD, open/save, play/stop, instancing, exports |
| Node | 17 | Add/delete/move/rename nodes, properties, signals, groups, selection |
| Script | 7 | Script CRUD, editing, attaching, validation |
| Editor | 12 | Errors, output log, screenshots, editor scripts, 3D camera, plugin reload |
| Input | 7 | Key/mouse/action simulation, sequences, input map |
| Runtime | 19 | Live game inspection, recording/replay, UI probing, movement |
| Animation | 6 | Animation creation, tracks, keyframes |
| AnimationTree | 8 | State machines, transitions, blend trees |
| TileMap | 6 | Cell operations, fills, tile info |
| Theme | 7 | Theme resources, colors, fonts, styleboxes, Control layout |
| Profiling | 2 | Game and editor performance monitors |
| Batch | 10 | Bulk operations, cross-scene refactoring, dependency analysis |
| Shader | 6 | Shader creation, editing, materials, parameters |
| Export | 3 | Export presets and info |
| Resource | 6 | Resource CRUD, previews, autoloads |
| Physics | 6 | Bodies, collisions, layers, raycasts |
| 3D Scene | 6 | Meshes, cameras, lights, environment, GridMap, materials |
| Particle | 5 | Particle systems, gradients, presets |
| Navigation | 5 | Regions, agents, baking, layers |
| Audio | 6 | Players, buses, effects, bus layout |
| Testing | 6 | Automated scenarios, assertions, stress tests |
| Android | 3 | Device management, presets, deployment |
| Analysis | 4 | Scene complexity, signal flow, unused resources, statistics |

> The 175 tools map onto 174 distinct Godot plugin commands (one command is exposed by
> two tools). Compact mode reaches the same 174 commands through 22 umbrella tools.

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
- Request timeout is 30 seconds by default; a few long-running tools raise it
  (e.g. `move_to`, `replay_recording`, `bake_navigation_mesh`)

### `bake_navigation_mesh` appears to hang
- The Godot plugin uses a deprecated baking API that blocks the editor main thread on
  some Godot 4.7 builds. The tool waits up to 120s; if the editor stays frozen you will
  need to restart it.

## License

MIT - Free to use and modify.