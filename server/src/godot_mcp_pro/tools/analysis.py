"""Analysis and search tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def analyze_scene_complexity(path: str = "") -> dict[str, Any]:
        """Analyze scene performance metrics (node count, depth, resources, etc.).

        Args:
            path: Scene path to analyze (empty = current scene)
        """
        return await bridge.call_godot("analyze_scene_complexity", {"path": path})

    @mcp.tool()
    async def analyze_signal_flow(node_path: str = "") -> dict[str, Any]:
        """Map all signal connections in the scene as a flow graph.

        Args:
            node_path: Root node to analyze (empty = scene root)
        """
        return await bridge.call_godot("analyze_signal_flow", {"node_path": node_path})

    @mcp.tool()
    async def find_unused_resources(
        path: str = "res://",
        include_addons: bool = False,
    ) -> dict[str, Any]:
        """Find resources that are not referenced by any scene or script.

        Args:
            path: Directory to scan (default "res://")
            include_addons: Whether to also scan res://addons (default False)
        """
        return await bridge.call_godot("find_unused_resources", {
            "path": path,
            "include_addons": include_addons,
        })

    @mcp.tool()
    async def get_project_statistics(
        path: str = "res://",
        include_addons: bool = False,
    ) -> dict[str, Any]:
        """Get project-wide statistics (file counts, scene counts, script metrics, etc.).

        Args:
            path: Directory to analyze (default "res://")
            include_addons: Whether to also count res://addons (default False)
        """
        return await bridge.call_godot("get_project_statistics", {
            "path": path,
            "include_addons": include_addons,
        })
