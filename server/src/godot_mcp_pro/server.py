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
_port_env = os.environ.get("GODOT_MCP_PORT", "")
GODOT_MCP_PORT = int(_port_env) if _port_env else 6505
# If user explicitly set a port, don't retry other ports
_port_explicit = bool(_port_env)
GODOT_MCP_LOG_LEVEL = os.environ.get("GODOT_MCP_LOG_LEVEL", "INFO")

# Compact mode: fewer tools (22 instead of 175) for weaker LLMs / token savings
COMPACT_MODE = "--compact" in sys.argv
while "--compact" in sys.argv:
    sys.argv.remove("--compact")

# Global bridge instance
bridge = GodotBridge(port=GODOT_MCP_PORT, port_retry=True)


@asynccontextmanager
async def lifespan(app):
    """FastMCP lifespan - start/stop the WebSocket bridge."""
    await bridge.start()
    logger.info(
        f"Godot MCP Pro started. Waiting for Godot on ws://127.0.0.1:{bridge.port}"
    )
    try:
        yield
    finally:
        await bridge.stop()


# Create FastMCP server
_instructions_full = (
    "Godot MCP Pro - AI-powered Godot game development server. "
    "Provides 175 tools for scene management, node manipulation, scripting, "
    "animation, physics, audio, and more. "
    "Requires Godot editor to be running with the MCP plugin enabled."
)
_instructions_compact = (
    "Godot MCP Pro (compact mode) - AI-powered Godot game development server. "
    "Provides 22 domain tools (project, scene, node, script, editor, input, "
    "runtime, animation, tilemap, ui, physics, scene_3d, particles, navigation, "
    "audio, shader, resource, batch, test, export, diagnostics) + batch_execute. "
    "Each tool takes an 'action' string and a 'params' dict. "
    "Requires Godot editor to be running with the MCP plugin enabled."
)

mcp = FastMCP(
    "godot-mcp-pro",
    instructions=_instructions_compact if COMPACT_MODE else _instructions_full,
    lifespan=lifespan,
)


def _register_all_tools():
    """Register all tool modules."""
    if COMPACT_MODE:
        from .tools import compact
        compact.register(mcp, bridge)
        logger.info("Compact mode: registered 22 tools")
    else:
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
        logger.info("Full mode: registered 175 tools")


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