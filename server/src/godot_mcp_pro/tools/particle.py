"""Particle system tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def create_particles(
        parent_path: str = ".",
        is_3d: bool = False,
        name: str = "",
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a GPUParticles2D or GPUParticles3D node.

        Args:
            parent_path: Path to parent node
            is_3d: Whether to create 3D particles (default False = 2D)
            name: Optional name for the node
            properties: Particle properties (amount, lifetime, explosiveness, etc.)
        """
        return await bridge.call_godot("create_particles", {
            "parent_path": parent_path,
            "is_3d": is_3d,
            "name": name,
            "properties": properties or {},
        })

    @mcp.tool()
    async def set_particle_material(
        node_path: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure a ParticleProcessMaterial on a particles node.

        Args:
            node_path: Path to the particles node
            properties: Material properties (direction, spread, gravity, velocity, etc.)
        """
        return await bridge.call_godot("set_particle_material", {
            "node_path": node_path,
            "properties": properties or {},
        })

    @mcp.tool()
    async def set_particle_color_gradient(
        node_path: str,
        colors: list[str],
        offsets: list[float] | None = None,
    ) -> dict[str, Any]:
        """Set a color gradient for a particle system.

        Args:
            node_path: Path to the particles node
            colors: List of color values (hex "#ff0000" or color names)
            offsets: Optional list of gradient offsets (0.0-1.0)
        """
        return await bridge.call_godot("set_particle_color_gradient", {
            "node_path": node_path,
            "colors": colors,
            "offsets": offsets or [],
        })

    @mcp.tool()
    async def apply_particle_preset(
        node_path: str,
        preset: str,
    ) -> dict[str, Any]:
        """Apply a particle preset (fire, smoke, sparks, snow, rain, explosion, etc.).

        Args:
            node_path: Path to the particles node
            preset: Preset name ("fire", "smoke", "sparks", "snow", "rain", "explosion", "magic", "dust")
        """
        return await bridge.call_godot("apply_particle_preset", {
            "node_path": node_path,
            "preset": preset,
        })

    @mcp.tool()
    async def get_particle_info(node_path: str) -> dict[str, Any]:
        """Get detailed info about a particle system.

        Args:
            node_path: Path to the particles node
        """
        return await bridge.call_godot("get_particle_info", {"node_path": node_path})