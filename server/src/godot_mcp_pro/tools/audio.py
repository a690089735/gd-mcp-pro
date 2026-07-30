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
        player_type: str = "",
    ) -> dict[str, Any]:
        """Add an AudioStreamPlayer, AudioStreamPlayer2D, or AudioStreamPlayer3D.

        Args:
            parent_path: Path to the parent node
            name: Node name (required by the engine; defaults to "AudioPlayer")
            stream_path: res:// path to an AudioStream (.wav, .ogg, .mp3)
            is_3d: Use AudioStreamPlayer3D (ignored when player_type is given)
            properties: Any of: volume_db (float), bus (str), autoplay (bool),
                max_distance (float, 2D/3D), attenuation (float, 2D),
                attenuation_model (int, 3D), unit_size (float, 3D)
            player_type: Explicit class: "AudioStreamPlayer",
                "AudioStreamPlayer2D", or "AudioStreamPlayer3D"
        """
        params: dict[str, Any] = {
            **(properties or {}),
            "node_path": parent_path,
            "name": name or "AudioPlayer",
        }
        params["type"] = player_type or (
            "AudioStreamPlayer3D" if is_3d else "AudioStreamPlayer"
        )
        if stream_path:
            params["stream"] = stream_path
        return await bridge.call_godot("add_audio_player", params)

    @mcp.tool()
    async def add_audio_bus(
        name: str,
        send: str = "Master",
        volume_db: float | None = None,
        mute: bool | None = None,
        solo: bool | None = None,
        at_position: int = -1,
    ) -> dict[str, Any]:
        """Add a new audio bus.

        Args:
            name: Name for the new bus
            send: Bus to send output to (default "Master")
            volume_db: Optional initial volume in dB
            mute: Optional initial mute state
            solo: Optional initial solo state
            at_position: Insert index (-1 = append)
        """
        params: dict[str, Any] = {"name": name, "send": send}
        if volume_db is not None:
            params["volume_db"] = volume_db
        if mute is not None:
            params["mute"] = mute
        if solo is not None:
            params["solo"] = solo
        if at_position >= 0:
            params["at_position"] = at_position
        return await bridge.call_godot("add_audio_bus", params)

    @mcp.tool()
    async def add_audio_bus_effect(
        bus: str,
        effect_type: str,
        properties: dict[str, Any] | None = None,
        at_position: int = -1,
    ) -> dict[str, Any]:
        """Add an effect to an audio bus.

        Args:
            bus: Bus name to add the effect to
            effect_type: "reverb", "delay", "chorus", "distortion", "eq",
                "compressor", or "limiter"
            properties: Effect-specific parameters, e.g.
                reverb: room_size, damping, spread, dry, wet, predelay_msec;
                delay: dry, tap1_active, tap1_delay_ms, tap1_level_db,
                    tap2_active, tap2_delay_ms, tap2_level_db, feedback;
                chorus: voice_count, dry, wet, rate_hz, depth;
                distortion: mode, drive, pre_gain, post_gain, keep_hf_hz;
                eq: gain, cutoff_hz, resonance, range_min_hz, range_max_hz;
                compressor: threshold, ratio, gain, attack_us, release_ms, mix;
                limiter: ceiling_db, threshold_db, soft_clip_db, soft_clip_ratio
            at_position: Insert index within the bus effect chain (-1 = append)
        """
        params: dict[str, Any] = {"bus": bus, "effect_type": effect_type}
        # GDScript reads a nested dictionary named "params" here (not flattened).
        if properties:
            params["params"] = properties
        if at_position >= 0:
            params["at_position"] = at_position
        return await bridge.call_godot("add_audio_bus_effect", params)

    @mcp.tool()
    async def set_audio_bus(
        bus: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure audio bus properties.

        Args:
            bus: Bus name to configure
            properties: Any of: volume_db (float), mute (bool), solo (bool),
                bypass_effects (bool), send (str, bus to route to),
                rename (str, new bus name)
        """
        return await bridge.call_godot("set_audio_bus", {
            **(properties or {}),
            "name": bus,
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