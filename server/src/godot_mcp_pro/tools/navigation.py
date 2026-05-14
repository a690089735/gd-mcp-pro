"""Navigation tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def setup_navigation_region(
        node_path: str = "",
        parent_path: str = ".",
        is_3d: bool = False,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure a NavigationRegion2D/3D node.

        Args:
            node_path: Path to existing node (empty = create new)
            parent_path: Parent path for new node (default ".")
            is_3d: Whether to use 3D navigation (default False)
            properties: Navigation mesh properties (cell_size, agent_radius, etc.)
        """
        return await bridge.call_godot("setup_navigation_region", {
            "node_path": node_path,
            "parent_path": parent_path,
            "is_3d": is_3d,
            "properties": properties or {},
        })

    @mcp.tool()
    async def setup_navigation_agent(
        node_path: str = "",
        parent_path: str = ".",
        is_3d: bool = False,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure a NavigationAgent2D/3D node.

        Args:
            node_path: Path to existing node (empty = create new)
            parent_path: Parent path for new node (default ".")
            is_3d: Whether to use 3D navigation (default False)
            properties: Agent properties (radius, max_speed, path_desired_distance, etc.)
        """
        return await bridge.call_godot("setup_navigation_agent", {
            "node_path": node_path,
            "parent_path": parent_path,
            "is_3d": is_3d,
            "properties": properties or {},
        })

    @mcp.tool()
    async def bake_navigation_mesh(node_path: str) -> dict[str, Any]:
        """Bake the navigation mesh for a NavigationRegion.

        Args:
            node_path: Path to the NavigationRegion node
        """
        return await bridge.call_godot("bake_navigation_mesh", {"node_path": node_path})

    @mcp.tool()
    async def set_navigation_layers(
        node_path: str,
        layers: int,
    ) -> dict[str, Any]:
        """Set navigation layers on a navigation node.

        Args:
            node_path: Path to the navigation node
            layers: Navigation layers bitmask
        """
        return await bridge.call_godot("set_navigation_layers", {
            "node_path": node_path,
            "layers": layers,
        })

    @mcp.tool()
    async def get_navigation_info(node_path: str = "") -> dict[str, Any]:
        """Get navigation setup info for the scene.

        Args:
            node_path: Path to specific node (empty = scene overview)
        """
        return await bridge.call_godot("get_navigation_info", {"node_path": node_path})