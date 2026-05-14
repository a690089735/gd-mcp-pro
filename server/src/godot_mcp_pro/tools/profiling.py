"""Profiling tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def get_performance_monitors() -> dict[str, Any]:
        """Get all performance monitors (FPS, memory, physics, draw calls, etc.)."""
        return await bridge.call_godot("get_performance_monitors")

    @mcp.tool()
    async def get_editor_performance() -> dict[str, Any]:
        """Get a quick performance summary of the editor."""
        return await bridge.call_godot("get_editor_performance")