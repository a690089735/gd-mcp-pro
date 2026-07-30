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
            properties: Any of: amount (int), lifetime (float),
                explosiveness (float 0-1), randomness (float 0-1),
                one_shot (bool), emitting (bool)
        """
        return await bridge.call_godot("create_particles", {
            **(properties or {}),
            "parent_path": parent_path,
            "is_3d": is_3d,
            "name": name,
        })

    @mcp.tool()
    async def set_particle_material(
        node_path: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure a ParticleProcessMaterial on a particles node.

        Args:
            node_path: Path to the particles node
            properties: Any of: direction ({x,y,z}), spread, gravity ({x,y,z}),
                initial_velocity_min, initial_velocity_max,
                angular_velocity_min, angular_velocity_max,
                orbit_velocity_min, orbit_velocity_max,
                damping_min, damping_max, scale_min, scale_max, color,
                emission_shape ("point"/"sphere"/"sphere_surface"/"box"/"ring"),
                emission_sphere_radius, emission_box_extents ({x,y,z}),
                emission_ring_radius, emission_ring_inner_radius,
                emission_ring_height, attractor_interaction_enabled (bool)
        """
        return await bridge.call_godot("set_particle_material", {
            **(properties or {}),
            "node_path": node_path,
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
            offsets: Optional list of gradient offsets (0.0-1.0).
                If omitted, colors are spread evenly from 0.0 to 1.0.
        """
        if not colors:
            return {"error": {"code": -32602, "message": "colors must not be empty"}}

        if offsets:
            paired = list(zip(offsets, colors))
        elif len(colors) == 1:
            paired = [(0.0, colors[0])]
        else:
            step = 1.0 / (len(colors) - 1)
            paired = [(i * step, c) for i, c in enumerate(colors)]

        stops = [{"offset": float(o), "color": c} for o, c in paired]
        return await bridge.call_godot("set_particle_color_gradient", {
            "node_path": node_path,
            "stops": stops,
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