"""Node manipulation tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def add_node(
        type: str,
        parent_path: str = ".",
        name: str = "",
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a new node to the scene tree.

        Args:
            type: Node type to create (e.g. "CharacterBody2D", "Sprite2D")
            parent_path: Path of parent node (default "." for scene root)
            name: Optional name for the new node
            properties: Optional dictionary of properties to set on creation
        """
        return await bridge.call_godot("add_node", {
            "type": type,
            "parent_path": parent_path,
            "name": name,
            "properties": properties or {},
        })

    @mcp.tool()
    async def delete_node(node_path: str) -> dict[str, Any]:
        """Delete a node from the scene (supports undo).

        Args:
            node_path: Path to the node to delete
        """
        return await bridge.call_godot("delete_node", {"node_path": node_path})

    @mcp.tool()
    async def duplicate_node(node_path: str, name: str = "") -> dict[str, Any]:
        """Duplicate a node and its children.

        Args:
            node_path: Path to the node to duplicate
            name: Optional name for the duplicated node
        """
        return await bridge.call_godot("duplicate_node", {
            "node_path": node_path,
            "name": name,
        })

    @mcp.tool()
    async def move_node(node_path: str, new_parent_path: str) -> dict[str, Any]:
        """Move/reparent a node to a new parent.

        Args:
            node_path: Path to the node to move
            new_parent_path: Path to the new parent node
        """
        return await bridge.call_godot("move_node", {
            "node_path": node_path,
            "new_parent_path": new_parent_path,
        })

    @mcp.tool()
    async def update_property(
        node_path: str,
        property: str,
        value: Any,
    ) -> dict[str, Any]:
        """Set any property on a node. Supports smart type parsing for Vector2, Color, etc.

        Args:
            node_path: Path to the node
            property: Property name (e.g. "position", "modulate")
            value: Value to set (strings like "Vector2(100, 200)" are auto-parsed)
        """
        return await bridge.call_godot("update_property", {
            "node_path": node_path,
            "property": property,
            "value": value,
        })

    @mcp.tool()
    async def get_node_properties(
        node_path: str,
        category: str = "",
    ) -> dict[str, Any]:
        """Get all properties of a node.

        Args:
            node_path: Path to the node
            category: Optional category filter
        """
        return await bridge.call_godot("get_node_properties", {
            "node_path": node_path,
            "category": category,
        })

    @mcp.tool()
    async def add_resource(
        node_path: str,
        property: str,
        resource_type: str,
        resource_properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a resource (Shape, Material, etc.) to a node property.

        Args:
            node_path: Path to the node
            property: Property to set the resource on (e.g. "shape")
            resource_type: Resource type to create (e.g. "RectangleShape2D")
            resource_properties: Optional properties for the new resource
        """
        return await bridge.call_godot("add_resource", {
            "node_path": node_path,
            "property": property,
            "resource_type": resource_type,
            "resource_properties": resource_properties or {},
        })

    @mcp.tool()
    async def set_anchor_preset(
        node_path: str,
        preset: str,
        keep_offsets: bool = False,
    ) -> dict[str, Any]:
        """Set the anchor preset for a Control node.

        Args:
            node_path: Path to the Control node
            preset: Anchor preset name (e.g. "full_rect", "center", "top_left")
            keep_offsets: Whether to keep current offsets (default False)
        """
        return await bridge.call_godot("set_anchor_preset", {
            "node_path": node_path,
            "preset": preset,
            "keep_offsets": keep_offsets,
        })

    @mcp.tool()
    async def rename_node(node_path: str, new_name: str) -> dict[str, Any]:
        """Rename a node in the scene.

        Args:
            node_path: Path to the node to rename
            new_name: New name for the node
        """
        return await bridge.call_godot("rename_node", {
            "node_path": node_path,
            "new_name": new_name,
        })

    @mcp.tool()
    async def connect_signal(
        node_path: str,
        signal_name: str,
        target_path: str,
        method: str,
    ) -> dict[str, Any]:
        """Connect a signal between two nodes.

        Args:
            node_path: Path to the source node (emitter)
            signal_name: Name of the signal to connect
            target_path: Path to the target node (receiver)
            method: Method name to call on target
        """
        return await bridge.call_godot("connect_signal", {
            "source_path": node_path,
            "signal_name": signal_name,
            "target_path": target_path,
            "method_name": method,
        })

    @mcp.tool()
    async def disconnect_signal(
        node_path: str,
        signal_name: str,
        target_path: str,
        method: str,
    ) -> dict[str, Any]:
        """Disconnect a signal connection.

        Args:
            node_path: Path to the source node
            signal_name: Name of the signal
            target_path: Path to the target node
            method: Method name to disconnect
        """
        return await bridge.call_godot("disconnect_signal", {
            "source_path": node_path,
            "signal_name": signal_name,
            "target_path": target_path,
            "method_name": method,
        })

    @mcp.tool()
    async def get_node_groups(node_path: str) -> dict[str, Any]:
        """Get all groups a node belongs to.

        Args:
            node_path: Path to the node
        """
        return await bridge.call_godot("get_node_groups", {"node_path": node_path})

    @mcp.tool()
    async def set_node_groups(node_path: str, groups: list[str]) -> dict[str, Any]:
        """Set the group membership of a node.

        Args:
            node_path: Path to the node
            groups: List of group names to assign
        """
        return await bridge.call_godot("set_node_groups", {
            "node_path": node_path,
            "groups": groups,
        })

    @mcp.tool()
    async def find_nodes_in_group(group: str) -> dict[str, Any]:
        """Find all nodes that belong to a specific group.

        Args:
            group: Group name to search for
        """
        return await bridge.call_godot("find_nodes_in_group", {"group": group})