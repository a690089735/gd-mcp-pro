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
            properties: Any of: mass, gravity_scale, linear_damp, angular_damp,
                freeze (bool), freeze_mode, contact_monitor (bool),
                max_contacts_reported (int), continuous_cd, physics_material_override,
                floor_max_angle, floor_snap_length, floor_stop_on_slope (bool),
                max_slides (int), motion_mode, slide_on_ceiling (bool),
                wall_min_slide_angle
        """
        return await bridge.call_godot("setup_physics_body", {
            **(properties or {}),
            "node_path": node_path,
        })

    @mcp.tool()
    async def setup_collision(
        node_path: str,
        shape_type: str,
        shape_properties: dict[str, Any] | None = None,
        dimension: str = "",
    ) -> dict[str, Any]:
        """Add collision shapes to a node.

        Args:
            node_path: Path to the node (physics body or area)
            shape_type: Shape name. 2D: "rectangle"/"rect", "circle", "capsule",
                "segment", "custom". 3D: "box"/"rectangle"/"rect", "sphere"/"circle",
                "capsule", "cylinder", "custom"
            shape_properties: Any of: width, height, depth, radius (floats),
                ax, ay, bx, by (segment endpoints, 2D), points (list of [x,y] for
                "custom"), disabled (bool), one_way_collision (bool, 2D only)
            dimension: Force "2d" or "3d" (empty = auto-detect from the node type)
        """
        params: dict[str, Any] = {
            **(shape_properties or {}),
            "node_path": node_path,
            "shape": shape_type,
        }
        if dimension:
            params["dimension"] = dimension
        return await bridge.call_godot("setup_collision", params)

    @mcp.tool()
    async def set_physics_layers(
        node_path: str,
        layer: int | list[int] | None = None,
        mask: int | list[int] | None = None,
    ) -> dict[str, Any]:
        """Set collision layer and mask for a physics node.

        Args:
            node_path: Path to the physics node
            layer: Collision layer, either a raw bitmask int (5 = layers 1+3)
                or a list of 1-based layer numbers ([1, 3])
            mask: Collision mask, same formats as `layer`
        """
        params: dict[str, Any] = {"node_path": node_path}
        if layer is not None:
            params["collision_layer"] = layer
        if mask is not None:
            params["collision_mask"] = mask
        return await bridge.call_godot("set_physics_layers", params)

    @mcp.tool()
    async def get_physics_layers(node_path: str) -> dict[str, Any]:
        """Get collision layer and mask info for a physics node.

        Args:
            node_path: Path to the physics node
        """
        return await bridge.call_godot("get_physics_layers", {"node_path": node_path})

    @mcp.tool()
    async def get_collision_info(
        node_path: str,
        include_children: bool = True,
    ) -> dict[str, Any]:
        """Get collision shape details for a node.

        Args:
            node_path: Path to the node with collision shapes
            include_children: Also report shapes on descendant nodes (default True)
        """
        return await bridge.call_godot("get_collision_info", {
            "node_path": node_path,
            "include_children": include_children,
        })

    @mcp.tool()
    async def add_raycast(
        node_path: str,
        target_x: float = 0,
        target_y: float | None = None,
        target_z: float = 0,
        is_3d: bool | None = None,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a RayCast2D or RayCast3D node.

        Args:
            node_path: Path to the parent node
            target_x: Ray target X (default 0)
            target_y: Ray target Y (default 50 for 2D / -1 for 3D)
            target_z: Ray target Z (3D only, default 0)
            is_3d: Force RayCast3D (True) or RayCast2D (False).
                None = auto-detect from the parent node's dimension.
            properties: Any of: name (str, default "RayCast"), enabled (bool),
                collision_mask (int), collide_with_areas (bool),
                collide_with_bodies (bool), hit_from_inside (bool)
        """
        params: dict[str, Any] = {
            **(properties or {}),
            "node_path": node_path,
            "target_x": target_x,
            "target_z": target_z,
        }
        if is_3d is not None:
            params["dimension"] = "3d" if is_3d else "2d"
        if target_y is not None:
            params["target_y"] = target_y
        return await bridge.call_godot("add_raycast", params)

