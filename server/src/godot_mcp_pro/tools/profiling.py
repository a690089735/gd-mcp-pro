"""Profiling tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def get_performance_monitors() -> dict[str, Any]:
        """Get the RUNNING GAME's performance monitors (FPS, memory, physics, draw calls, etc.).

        Requires a playing scene (use play_scene first) — `Performance` is a
        per-process singleton, so metrics are routed through the game IPC channel
        and the response carries "process": "game".
        For editor-process metrics use get_editor_performance instead.
        """
        return await bridge.call_godot("get_performance_monitors")

    @mcp.tool()
    async def get_editor_performance() -> dict[str, Any]:
        """Get a quick performance summary of the editor process (no running game needed)."""
        return await bridge.call_godot("get_editor_performance")