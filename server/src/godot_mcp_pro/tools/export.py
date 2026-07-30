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
    async def export_project(
        preset: str = "",
        preset_index: int = -1,
        debug: bool = True,
    ) -> dict[str, Any]:
        """Get the export command for a specific preset.

        Args:
            preset: Name of the export preset to use (empty = use preset_index)
            preset_index: Preset index to use when preset name is empty (-1 = first)
            debug: Build a debug export (default True)
        """
        params: dict[str, Any] = {"debug": debug}
        if preset:
            params["preset_name"] = preset
        if preset_index >= 0:
            params["preset_index"] = preset_index
        return await bridge.call_godot("export_project", params)

    @mcp.tool()
    async def get_export_info() -> dict[str, Any]:
        """Get export-related project info including templates and presets."""
        return await bridge.call_godot("get_export_info")