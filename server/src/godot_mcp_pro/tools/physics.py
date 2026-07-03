"""Physics tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def setup_physics_body(
        node_path: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure physics body properties (gravity, mass, friction, etc.).

        Args:
            node_path: Path to the physics body node
            properties: Physics properties to set (gravity_scale, mass, friction, etc.)
        """
        return await bridge.call_godot("setup_physics_body", {
            "node_path": node_path,
            "properties": properties or {},
        })

    @mcp.tool()
    async def setup_collision(
        node_path: str,
        shape_type: str,
        shape_properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add collision shapes to a node.

        Args:
            node_path: Path to the node (physics body or area)
            shape_type: Shape type (e.g. "rectangle", "circle", "capsule", "box", "sphere")
            shape_properties: Shape properties (size, radius, height, etc.)
        """
        return await bridge.call_godot("setup_collision", {
            "node_path": node_path,
            "shape_type": shape_type,
            "shape_properties": shape_properties or {},
        })

    @mcp.tool()
    async def set_physics_layers(
        node_path: str,
        layer: int | None = None,
        mask: int | None = None,
    ) -> dict[str, Any]:
        """Set collision layer and mask for a physics node.

        Args:
            node_path: Path to the physics node
            layer: Collision layer value (bitmask)
            mask: Collision mask value (bitmask)
        """
        params: dict[str, Any] = {"node_path": node_path}
        if layer is not None:
            params["layer"] = layer
        if mask is not None:
            params["mask"] = mask
        return await bridge.call_godot("set_physics_layers", params)

    @mcp.tool()
    async def get_physics_layers(node_path: str) -> dict[str, Any]:
        """Get collision layer and mask info for a physics node.

        Args:
            node_path: Path to the physics node
        """
        return await bridge.call_godot("get_physics_layers", {"node_path": node_path})

    @mcp.tool()
    async def get_collision_info(node_path: str) -> dict[str, Any]:
        """Get collision shape details for a node.

        Args:
            node_path: Path to the node with collision shapes
        """
        return await bridge.call_godot("get_collision_info", {"node_path": node_path})

    @mcp.tool()
    async def add_raycast(
        node_path: str,
        target_x: float = 0,
        target_y: float = -50,
        target_z: float = 0,
        is_3d: bool = False,
    ) -> dict[str, Any]:
        """Add a RayCast2D or RayCast3D node.

        Args:
            node_path: Path to the parent node
            target_x: Ray target X
            target_y: Ray target Y
            target_z: Ray target Z (3D only)
            is_3d: Whether to create RayCast3D (default False = RayCast2D)
        """
        return await bridge.call_godot("add_raycast", {
            "node_path": node_path,
            "target_x": target_x,
            "target_y": target_y,
            "target_z": target_z,
            "is_3d": is_3d,
        })

