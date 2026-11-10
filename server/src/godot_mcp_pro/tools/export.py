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

    @mcp.tool()
    async def export_patch_pck(
        output_path: str,
        preset: str = "",
        preset_index: int = -1,
        patches: list[str] | None = None,
        timeout_sec: float = 300.0,
    ) -> dict[str, Any]:
        """Export a patch PCK against base packs via `godot --headless --export-patch`.

        Release mode only. Writes to a temp file, validates it and only then
        replaces output_path, so an existing pack is never destroyed. Refuses to
        write over any base pack. Unsaved scenes are exported as last saved.

        Args:
            output_path: Destination .pck (res://, user:// or absolute; the
                directory must exist)
            preset: Export preset name (empty = use preset_index)
            preset_index: Preset index when preset is empty (-1 = first)
            patches: Base .pck files the game already ships (empty = use the
                preset's Patches list)
            timeout_sec: Max seconds for queueing + export (default 300, 10-1800)
        """
        params: dict[str, Any] = {"output_path": output_path}
        if preset:
            params["preset_name"] = preset
        if preset_index >= 0:
            params["preset_index"] = preset_index
        if patches:
            params["patches"] = patches
        if timeout_sec != 300.0:
            params["timeout_sec"] = timeout_sec
        # Godot clamps timeout_sec to 10..1800; stay above its own deadline.
        effective_timeout = min(max(timeout_sec, 10.0), 1800.0)
        return await bridge.call_godot(
            "export_patch_pck", params, timeout=effective_timeout + 30.0
        )