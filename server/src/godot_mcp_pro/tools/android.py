"""Android deployment tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def list_android_devices() -> dict[str, Any]:
        """List connected Android devices via ADB."""
        return await bridge.call_godot("list_android_devices")

    @mcp.tool()
    async def get_android_preset_info(
        preset: str = "",
    ) -> dict[str, Any]:
        """Get detailed information about Android export presets.

        Args:
            preset: Preset name to query (empty = first Android preset)
        """
        return await bridge.call_godot("get_android_preset_info", {
            "preset": preset,
        })

    @mcp.tool()
    async def deploy_to_android(
        device_serial: str = "",
        preset: str = "",
    ) -> dict[str, Any]:
        """Deploy the project to an Android device (export, install, and launch).

        Args:
            device_serial: Target device serial (empty = first available)
            preset: Export preset name to use (empty = first Android preset)
        """
        return await bridge.call_godot("deploy_to_android", {
            "device_serial": device_serial,
            "preset": preset,
        })
