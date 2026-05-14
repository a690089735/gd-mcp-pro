"""Main FastMCP server for Godot MCP Pro.

This server:
1. Starts a WebSocket server on the configured port (default 6505)
2. Waits for the Godot editor plugin to connect
3. Exposes MCP tools that forward commands to Godot via WebSocket
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from .bridge import GodotBridge

logger = logging.getLogger(__name__)

# Configuration from environment
GODOT_MCP_PORT = int(os.environ.get("GODOT_MCP_PORT", "6505"))
GODOT_MCP_LOG_LEVEL = os.environ.get("GODOT_MCP_LOG_LEVEL", "INFO")

# Global bridge instance
bridge = GodotBridge(port=GODOT_MCP_PORT)


@asynccontextmanager
async def lifespan(app):
    """FastMCP lifespan - start/stop the WebSocket bridge."""
    await bridge.start()
    logger.info(
        f"Godot MCP Pro started. Waiting for Godot on ws://127.0.0.1:{GODOT_MCP_PORT}"
    )
    try:
        yield
    finally:
        await bridge.stop()


# Create FastMCP server
mcp = FastMCP(
    "godot-mcp-pro",
    instructions=(
        "Godot MCP Pro - AI-powered Godot game development server. "
        "Provides 172 tools for scene management, node manipulation, scripting, "
        "animation, physics, audio, and more. "
        "Requires Godot editor to be running with the MCP plugin enabled."
    ),
    lifespan=lifespan,
)


def _register_all_tools():
    """Register all tool modules."""
    from .tools import (
        analysis,
        android,
        animation,
        audio,
        batch,
        editor,
        export,
        input_tools,
        navigation,
        node,
        particle,
        physics,
        profiling,
        project,
        resource,
        runtime,
        scene,
        scene_3d,
        script,
        shader,
        test,
        theme,
        tilemap,
    )

    # Each module registers its tools via register(mcp, bridge)
    project.register(mcp, bridge)
    scene.register(mcp, bridge)
    node.register(mcp, bridge)
    script.register(mcp, bridge)
    editor.register(mcp, bridge)
    input_tools.register(mcp, bridge)
    runtime.register(mcp, bridge)
    animation.register(mcp, bridge)
    tilemap.register(mcp, bridge)
    theme.register(mcp, bridge)
    profiling.register(mcp, bridge)
    batch.register(mcp, bridge)
    shader.register(mcp, bridge)
    export.register(mcp, bridge)
    resource.register(mcp, bridge)
    physics.register(mcp, bridge)
    scene_3d.register(mcp, bridge)
    particle.register(mcp, bridge)
    navigation.register(mcp, bridge)
    audio.register(mcp, bridge)
    test.register(mcp, bridge)
    android.register(mcp, bridge)
    analysis.register(mcp, bridge)


# Register tools at import time
_register_all_tools()


def main():
    """Entry point for the MCP server."""
    logging.basicConfig(
        level=getattr(logging, GODOT_MCP_LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    # Run MCP server (stdio transport)
    mcp.run()


if __name__ == "__main__":
    main()