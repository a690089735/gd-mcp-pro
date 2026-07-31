"""3D Scene tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge

# GDScript expects the concrete Godot class names; accept friendly aliases too.
_MESH_TYPES = {
    "box": "BoxMesh",
    "cube": "BoxMesh",
    "sphere": "SphereMesh",
    "cylinder": "CylinderMesh",
    "capsule": "CapsuleMesh",
    "plane": "PlaneMesh",
    "prism": "PrismMesh",
    "torus": "TorusMesh",
    "quad": "QuadMesh",
}

_LIGHT_TYPES = {
    "directional": "DirectionalLight3D",
    "sun": "DirectionalLight3D",
    "omni": "OmniLight3D",
    "point": "OmniLight3D",
    "spot": "SpotLight3D",
}


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def add_mesh_instance(
        parent_path: str = ".",
        mesh_type: str = "box",
        name: str = "",
        properties: dict[str, Any] | None = None,
        mesh_file: str = "",
    ) -> dict[str, Any]:
        """Add a MeshInstance3D with a primitive mesh or an imported mesh file.

        Args:
            parent_path: Path to parent node (default "." for root)
            mesh_type: Primitive mesh: "box", "sphere", "cylinder", "capsule",
                "plane", "prism", "torus", "quad" (or the Godot class name
                directly, e.g. "BoxMesh"). Ignored when mesh_file is given.
            name: Optional name for the node
            properties: Mesh resource properties applied to the primitive
                (e.g. size, radius, height, radial_segments)
            mesh_file: Optional res:// path to a .glb/.gltf/.obj/.mesh to load
                instead of creating a primitive
        """
        params: dict[str, Any] = {"parent_path": parent_path}
        if name:
            params["name"] = name
        if mesh_file:
            params["mesh_file"] = mesh_file
        else:
            params["mesh_type"] = _MESH_TYPES.get(mesh_type.lower(), mesh_type)
        if properties:
            params["mesh_properties"] = properties
        return await bridge.call_godot("add_mesh_instance", params)

    @mcp.tool()
    async def setup_camera_3d(
        node_path: str = "",
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure a Camera3D node's properties (creates one when node_path is empty).

        Args:
            node_path: Path to an existing Camera3D (empty = create a new one)
            properties: Any of: fov, near, far, size, projection
                ("perspective"/"orthogonal"/"frustum"), current (bool), cull_mask (int),
                environment_path, look_at ({x,y,z} or node path), rotation ({x,y,z}),
                position ({x,y,z}), name, parent_path
        """
        params: dict[str, Any] = {**(properties or {})}
        if node_path:
            params["node_path"] = node_path
        return await bridge.call_godot("setup_camera_3d", params)

    @mcp.tool()
    async def setup_lighting(
        light_type: str = "directional",
        parent_path: str = ".",
        name: str = "",
        properties: dict[str, Any] | None = None,
        preset: str = "",
    ) -> dict[str, Any]:
        """Add a light node (DirectionalLight3D, OmniLight3D, SpotLight3D).

        Args:
            light_type: "directional", "omni", "spot" (or the Godot class name
                directly, e.g. "DirectionalLight3D"). Ignored when preset is given.
            parent_path: Path to parent node
            name: Optional name for the light
            properties: Any of: color (hex or "Color(r,g,b)"), energy (float),
                shadows (bool), range (float, omni/spot), attenuation (float,
                omni/spot), spot_angle (float), spot_angle_attenuation (float),
                rotation ({x,y,z}), position ({x,y,z})
            preset: Shortcut config: "sun", "indoor", or "dramatic"
                (overrides light_type)
        """
        params: dict[str, Any] = {
            **(properties or {}),
            "parent_path": parent_path,
        }
        if name:
            params["name"] = name
        if preset:
            params["preset"] = preset
        else:
            params["light_type"] = _LIGHT_TYPES.get(light_type.lower(), light_type)
        return await bridge.call_godot("setup_lighting", params)

    @mcp.tool()
    async def setup_environment(
        node_path: str = "",
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure a WorldEnvironment node (creates one when node_path is empty).

        Args:
            node_path: Path to an existing WorldEnvironment (empty = create a new one)
            properties: Any of: background_mode,
                sky (nested dict — "sky_curve" and "sun_angle_max" live INSIDE it,
                e.g. {"sky": {"sky_curve": 0.15, "sun_angle_max": 30.0}}),
                ambient_light_source, ambient_light_color, ambient_light_energy,
                fog_enabled, fog_density, fog_light_color, fog_light_energy,
                glow_enabled, glow_intensity, glow_strength, glow_bloom,
                ssao_enabled, ssao_radius, ssao_intensity,
                ssr_enabled, ssr_max_steps, ssr_fade_in, ssr_fade_out,
                sdfgi_enabled, tonemap_mode, tonemap_exposure, tonemap_white,
                name, parent_path
        """
        params: dict[str, Any] = {**(properties or {})}
        if node_path:
            params["node_path"] = node_path
        return await bridge.call_godot("setup_environment", params)

    @mcp.tool()
    async def add_gridmap(
        parent_path: str = ".",
        name: str = "",
        mesh_library_path: str = "",
        node_path: str = "",
        cell_size: dict[str, float] | None = None,
        cells: list[dict[str, int]] | None = None,
    ) -> dict[str, Any]:
        """Create or configure a GridMap node.

        Args:
            parent_path: Path to parent node (used when creating a new GridMap)
            name: Optional name for the GridMap
            mesh_library_path: res:// path to a MeshLibrary (.meshlib/.tres)
            node_path: Path to an existing GridMap to configure instead of creating one
            cell_size: Cell size as {"x": .., "y": .., "z": ..}
            cells: Cells to set, each {"x", "y", "z", "item", "orientation"}
        """
        params: dict[str, Any] = {"parent_path": parent_path}
        if name:
            params["name"] = name
        if mesh_library_path:
            params["mesh_library_path"] = mesh_library_path
        if node_path:
            params["node_path"] = node_path
        if cell_size:
            params["cell_size"] = cell_size
        if cells:
            params["cells"] = cells
        return await bridge.call_godot("add_gridmap", params)

    @mcp.tool()
    async def set_material_3d(
        node_path: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Set StandardMaterial3D properties on a MeshInstance3D.

        Args:
            node_path: Path to the MeshInstance3D node
            properties: Any of: albedo_color, albedo_texture, metallic,
                metallic_texture, roughness, roughness_texture, normal_texture,
                emission (bool), emission_color, emission_energy, emission_texture,
                transparency, cull_mode, surface_index (int)
        """
        return await bridge.call_godot("set_material_3d", {
            **(properties or {}),
            "node_path": node_path,
        })