"""Audio tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def add_audio_player(
        parent_path: str = ".",
        name: str = "",
        stream_path: str = "",
        is_3d: bool = False,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add an AudioStreamPlayer, AudioStreamPlayer2D, or AudioStreamPlayer3D.

        Args:
            parent_path: Path to parent node
            name: Optional node name
            stream_path: Path to audio stream resource (.wav, .ogg, .mp3)
            is_3d: Whether to use 3D audio (default False)
            properties: Additional properties (volume_db, pitch_scale, bus, etc.)
        """
        return await bridge.call_godot("add_audio_player", {
            "parent_path": parent_path,
            "name": name,
            "stream_path": stream_path,
            "is_3d": is_3d,
            "properties": properties or {},
        })

    @mcp.tool()
    async def add_audio_bus(
        name: str,
        send: str = "Master",
    ) -> dict[str, Any]:
        """Add a new audio bus.

        Args:
            name: Name for the new bus
            send: Bus to send output to (default "Master")
        """
        return await bridge.call_godot("add_audio_bus", {
            "name": name,
            "send": send,
        })

    @mcp.tool()
    async def add_audio_bus_effect(
        bus: str,
        effect_type: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add an effect to an audio bus.

        Args:
            bus: Bus name to add effect to
            effect_type: Effect type ("reverb", "delay", "chorus", "distortion", "eq", "compressor", "limiter")
            properties: Effect-specific properties
        """
        return await bridge.call_godot("add_audio_bus_effect", {
            "bus": bus,
            "effect_type": effect_type,
            "properties": properties or {},
        })

    @mcp.tool()
    async def set_audio_bus(
        bus: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure audio bus properties.

        Args:
            bus: Bus name to configure
            properties: Bus properties (volume_db, mute, solo, send, etc.)
        """
        return await bridge.call_godot("set_audio_bus", {
            "bus": bus,
            "properties": properties or {},
        })

    @mcp.tool()
    async def get_audio_bus_layout() -> dict[str, Any]:
        """Get the complete audio bus layout info."""
        return await bridge.call_godot("get_audio_bus_layout")

    @mcp.tool()
    async def get_audio_info(node_path: str = "") -> dict[str, Any]:
        """Get audio-related node info.

        Args:
            node_path: Path to audio node (empty = scene overview)
        """
        return await bridge.call_godot("get_audio_info", {"node_path": node_path})