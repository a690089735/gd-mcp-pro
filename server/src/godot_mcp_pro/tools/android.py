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
        preset_index: int = -1,
    ) -> dict[str, Any]:
        """Get detailed information about Android export presets.

        Args:
            preset: Preset name to query (empty = first Android preset)
            preset_index: Preset index to query when preset name is empty
        """
        params: dict[str, Any] = {}
        if preset:
            params["preset_name"] = preset
        if preset_index >= 0:
            params["preset_index"] = preset_index
        return await bridge.call_godot("get_android_preset_info", params)

    @mcp.tool()
    async def deploy_to_android(
        device_serial: str = "",
        preset: str = "",
        preset_index: int = -1,
        debug: bool = True,
        launch: bool = True,
        skip_export: bool = False,
    ) -> dict[str, Any]:
        """Deploy the project to an Android device (export, install, and launch).

        Args:
            device_serial: Target device serial (empty = first available)
            preset: Export preset name to use (empty = first Android preset)
            preset_index: Preset index to use when preset name is empty
            debug: Build a debug APK (default True)
            launch: Launch the app after installing (default True)
            skip_export: Install the existing APK without re-exporting (default False)
        """
        params: dict[str, Any] = {
            "device_serial": device_serial,
            "debug": debug,
            "launch": launch,
            "skip_export": skip_export,
        }
        if preset:
            params["preset_name"] = preset
        if preset_index >= 0:
            params["preset_index"] = preset_index
        return await bridge.call_godot("deploy_to_android", params)
