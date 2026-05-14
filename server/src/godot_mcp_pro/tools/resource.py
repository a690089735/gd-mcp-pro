"""Resource management tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def read_resource(path: str) -> dict[str, Any]:
        """Read a .tres resource file and get its properties.

        Args:
            path: Path to the resource file (e.g. "res://resources/config.tres")
        """
        return await bridge.call_godot("read_resource", {"path": path})

    @mcp.tool()
    async def edit_resource(
        path: str,
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        """Edit properties of an existing resource file.

        Args:
            path: Path to the resource file
            properties: Dictionary of property names and values to set
        """
        return await bridge.call_godot("edit_resource", {
            "path": path,
            "properties": properties,
        })

    @mcp.tool()
    async def create_resource(
        path: str,
        type: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new .tres resource file.

        Args:
            path: Where to save the resource
            type: Resource type (e.g. "Resource", "StyleBoxFlat")
            properties: Optional initial properties
        """
        return await bridge.call_godot("create_resource", {
            "path": path,
            "type": type,
            "properties": properties or {},
        })

    @mcp.tool()
    async def get_resource_preview(path: str) -> dict[str, Any]:
        """Get a thumbnail preview of a resource.

        Args:
            path: Path to the resource file
        """
        return await bridge.call_godot("get_resource_preview", {"path": path})

    @mcp.tool()
    async def add_autoload(
        name: str,
        path: str,
    ) -> dict[str, Any]:
        """Register an autoload singleton.

        Args:
            name: Autoload name (e.g. "GameManager")
            path: Path to the script or scene (e.g. "res://scripts/game_manager.gd")
        """
        return await bridge.call_godot("add_autoload", {
            "name": name,
            "path": path,
        })

    @mcp.tool()
    async def remove_autoload(name: str) -> dict[str, Any]:
        """Remove an autoload singleton.

        Args:
            name: Autoload name to remove
        """
        return await bridge.call_godot("remove_autoload", {"name": name})