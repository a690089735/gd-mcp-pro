"""3D Scene tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def add_mesh_instance(
        parent_path: str = ".",
        mesh_type: str = "box",
        name: str = "",
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a MeshInstance3D with a primitive mesh.

        Args:
            parent_path: Path to parent node (default "." for root)
            mesh_type: Mesh type ("box", "sphere", "cylinder", "capsule", "plane", "prism")
            name: Optional name for the node
            properties: Optional mesh/node properties (size, radius, height, etc.)
        """
        return await bridge.call_godot("add_mesh_instance", {
            "parent_path": parent_path,
            "mesh_type": mesh_type,
            "name": name,
            "properties": properties or {},
        })

    @mcp.tool()
    async def setup_camera_3d(
        node_path: str = "",
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure a Camera3D node's properties.

        Args:
            node_path: Path to the Camera3D node (empty = create new)
            properties: Camera properties (fov, near, far, position, rotation, etc.)
        """
        return await bridge.call_godot("setup_camera_3d", {
            "node_path": node_path,
            "properties": properties or {},
        })

    @mcp.tool()
    async def setup_lighting(
        light_type: str = "directional",
        parent_path: str = ".",
        name: str = "",
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add or configure a light node (DirectionalLight3D, OmniLight3D, SpotLight3D).

        Args:
            light_type: Light type ("directional", "omni", "spot")
            parent_path: Path to parent node
            name: Optional name for the light
            properties: Light properties (color, energy, shadow, range, etc.)
        """
        return await bridge.call_godot("setup_lighting", {
            "light_type": light_type,
            "parent_path": parent_path,
            "name": name,
            "properties": properties or {},
        })

    @mcp.tool()
    async def setup_environment(
        node_path: str = "",
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure a WorldEnvironment node.

        Args:
            node_path: Path to WorldEnvironment (empty = create new)
            properties: Environment properties (background, ambient, fog, glow, etc.)
        """
        return await bridge.call_godot("setup_environment", {
            "node_path": node_path,
            "properties": properties or {},
        })

    @mcp.tool()
    async def add_gridmap(
        parent_path: str = ".",
        name: str = "",
        mesh_library_path: str = "",
    ) -> dict[str, Any]:
        """Set up a GridMap node.

        Args:
            parent_path: Path to parent node
            name: Optional name for the GridMap
            mesh_library_path: Path to MeshLibrary resource
        """
        return await bridge.call_godot("add_gridmap", {
            "parent_path": parent_path,
            "name": name,
            "mesh_library_path": mesh_library_path,
        })

    @mcp.tool()
    async def set_material_3d(
        node_path: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Set StandardMaterial3D properties on a MeshInstance3D.

        Args:
            node_path: Path to the MeshInstance3D node
            properties: Material properties (albedo_color, metallic, roughness, emission, etc.)
        """
        return await bridge.call_godot("set_material_3d", {
            "node_path": node_path,
            "properties": properties or {},
        })