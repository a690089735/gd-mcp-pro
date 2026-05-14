"""Export tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def list_export_presets() -> dict[str, Any]:
        """List all export presets configured in the project."""
        return await bridge.call_godot("list_export_presets")

    @mcp.tool()
    async def export_project(preset: str) -> dict[str, Any]:
        """Get the export command for a specific preset.

        Args:
            preset: Name of the export preset to use
        """
        return await bridge.call_godot("export_project", {"preset": preset})

    @mcp.tool()
    async def get_export_info() -> dict[str, Any]:
        """Get export-related project info including templates and presets."""
        return await bridge.call_godot("get_export_info")