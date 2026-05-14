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

The server will start a WebSocket server on port 6505 and wait for the Godot editor plugin to connect. Once connected, all 172 MCP tools become available to your AI assistant.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GODOT_MCP_PORT` | `6505` | WebSocket port for Godot to connect to |
| `GODOT_MCP_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## How It Works

1. The Python server starts a **WebSocket server** on the configured port
2. The Godot editor plugin (which acts as a WebSocket **client**) connects to this server
3. When the AI calls an MCP tool, the server:
   - Formats a JSON-RPC 2.0 request
   - Sends it to Godot via WebSocket
   - Waits for the response
   - Returns the result to the AI

## Tool Categories (172 tools total)

| Category | Count | Description |
|----------|-------|-------------|
| Project | 7 | Project metadata, filesystem, settings |
| Scene | 9 | Scene CRUD, play/stop, instancing |
| Node | 14 | Add/delete/move nodes, properties, signals |
| Script | 8 | Script CRUD, editing, validation |
| Editor | 9 | Errors, screenshots, editor scripts |
| Input | 7 | Key/mouse/action simulation |
| Runtime | 19 | Game inspection, recording, navigation |
| Animation | 6 | Animation creation, tracks, keyframes |
| AnimationTree | 8 | State machines, blend trees |
| TileMap | 6 | Cell operations, tile info |
| Theme | 6 | Colors, fonts, styleboxes |
| Profiling | 2 | Performance monitors |
| Batch | 8 | Bulk operations, refactoring |
| Shader | 6 | Shader creation and editing |
| Export | 3 | Export presets and info |
| Resource | 6 | Resource CRUD, autoloads |
| Physics | 6 | Bodies, collisions, raycasts |
| 3D Scene | 6 | Meshes, cameras, lights |
| Particle | 5 | Particle systems and presets |
| Navigation | 5 | Regions, agents, pathfinding |
| Audio | 6 | Players, buses, effects |
| Testing | 6 | Automated testing, assertions |
| Android | 3 | Device management, deployment |
| Analysis | 4 | Scene complexity, statistics |

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
- Request timeout is 30 seconds by default

## License

MIT - Free to use and modify.