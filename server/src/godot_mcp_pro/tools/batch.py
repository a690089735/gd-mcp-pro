"""Batch operations and refactoring tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def find_nodes_by_type(
        type: str,
        recursive: bool = True,
    ) -> dict[str, Any]:
        """Find all nodes of a specific type in the current scene.

        Args:
            type: Node type to search for (e.g. "Sprite2D", "CollisionShape2D")
            recursive: Whether to search recursively (default True)
        """
        return await bridge.call_godot("find_nodes_by_type", {
            "type": type,
            "recursive": recursive,
        })

    @mcp.tool()
    async def find_signal_connections(node_path: str = "") -> dict[str, Any]:
        """Find all signal connections in the current scene.

        Args:
            node_path: Root node to start from (empty = scene root)
        """
        return await bridge.call_godot("find_signal_connections", {"node_path": node_path})

    @mcp.tool()
    async def batch_set_property(
        type: str,
        property: str,
        value: Any,
        node_path: str = "",
    ) -> dict[str, Any]:
        """Set a property on all nodes of a specific type.

        Args:
            type: Node type to target (e.g. "Sprite2D")
            property: Property name to set
            value: Value to set (supports smart type parsing)
            node_path: Root node to start from (empty = scene root)
        """
        return await bridge.call_godot("batch_set_property", {
            "type": type,
            "property": property,
            "value": value,
            "node_path": node_path,
        })

    @mcp.tool()
    async def find_node_references(
        pattern: str,
        path: str = "res://",
    ) -> dict[str, Any]:
        """Search project files for a pattern (e.g. node name or path).

        Args:
            pattern: Search pattern
            path: Directory to search in (default "res://")
        """
        return await bridge.call_godot("find_node_references", {
            "pattern": pattern,
            "path": path,
        })

    @mcp.tool()
    async def get_scene_dependencies(path: str = "") -> dict[str, Any]:
        """Get resource dependencies of a scene.

        Args:
            path: Scene path (empty = current scene)
        """
        return await bridge.call_godot("get_scene_dependencies", {"path": path})

    @mcp.tool()
    async def cross_scene_set_property(
        type: str,
        property: str,
        value: Any,
        scene_paths: list[str] | None = None,
    ) -> dict[str, Any]:
        """Set a property across all scenes on nodes of a specific type.

        Args:
            type: Node type to target
            property: Property name to set
            value: Value to set
            scene_paths: List of scene paths (empty = all scenes)
        """
        return await bridge.call_godot("cross_scene_set_property", {
            "type": type,
            "property": property,
            "value": value,
            "scene_paths": scene_paths or [],
        })

    @mcp.tool()
    async def find_script_references(path: str) -> dict[str, Any]:
        """Find where a script or resource is used across the project.

        Args:
            path: Path to the script/resource to search for
        """
        return await bridge.call_godot("find_script_references", {"path": path})

    @mcp.tool()
    async def batch_add_nodes(
        nodes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Batch-add multiple nodes in a single operation.

        Args:
            nodes: Array of node definitions, each with:
                - type (str, required): Node class name (e.g. "Sprite2D")
                - parent_path (str, optional): Parent path (default ".")
                - name (str, optional): Node name
                - properties (dict, optional): Properties to set
        """
        return await bridge.call_godot("batch_add_nodes", {
            "nodes": nodes,
        })

    @mcp.tool()
    async def detect_circular_dependencies(path: str = "res://") -> dict[str, Any]:
        """Find circular scene dependencies in the project.

        Args:
            path: Directory to analyze (default "res://")
        """
        return await bridge.call_godot("detect_circular_dependencies", {"path": path})
