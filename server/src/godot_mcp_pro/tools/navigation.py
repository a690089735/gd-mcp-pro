"""Navigation tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def setup_navigation_region(
        parent_path: str = ".",
        mode: str = "auto",
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a NavigationRegion2D/3D node under a parent.

        Args:
            parent_path: Path of the node the region is added to (default ".")
            mode: "2d", "3d", or "auto" to detect from the parent (default "auto")
            properties: Any of: name (str), navigation_layers (int),
                cell_size, agent_radius (both 2D+3D);
                3D only: agent_height, agent_max_climb, agent_max_slope, cell_height;
                2D only: source_geometry_mode
                ("root_node"/"groups_with_children"/"groups_explicit")
        """
        return await bridge.call_godot("setup_navigation_region", {
            **(properties or {}),
            "node_path": parent_path,
            "mode": mode,
        })

    @mcp.tool()
    async def setup_navigation_agent(
        parent_path: str = ".",
        mode: str = "auto",
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a NavigationAgent2D/3D node under a parent.

        Args:
            parent_path: Path of the node the agent is added to (default ".")
            mode: "2d", "3d", or "auto" to detect from the parent (default "auto")
            properties: Any of: name (str), radius, max_speed, max_neighbors (int),
                neighbor_distance, path_desired_distance, target_desired_distance,
                avoidance_enabled (bool), navigation_layers (int)
        """
        return await bridge.call_godot("setup_navigation_agent", {
            **(properties or {}),
            "node_path": parent_path,
            "mode": mode,
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