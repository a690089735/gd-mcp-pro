"""Scene management tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def get_scene_tree(max_depth: int = -1) -> dict[str, Any]:
        """Get the live scene tree hierarchy of the currently open scene.

        Args:
            max_depth: Maximum depth to traverse (-1 for unlimited)
        """
        return await bridge.call_godot("get_scene_tree", {"max_depth": max_depth})

    @mcp.tool()
    async def get_scene_file_content(path: str) -> dict[str, Any]:
        """Get the raw .tscn file content of a scene.

        Args:
            path: Path to the scene file (e.g. "res://scenes/main.tscn")
        """
        return await bridge.call_godot("get_scene_file_content", {"path": path})

    @mcp.tool()
    async def create_scene(
        path: str,
        root_type: str = "Node2D",
        root_name: str = "",
    ) -> dict[str, Any]:
        """Create a new scene file.

        Args:
            path: Where to save the scene (e.g. "res://scenes/player.tscn")
            root_type: Type of root node (default "Node2D")
            root_name: Name for the root node (defaults to filename)
        """
        return await bridge.call_godot("create_scene", {
            "path": path,
            "root_type": root_type,
            "root_name": root_name,
        })

    @mcp.tool()
    async def open_scene(path: str) -> dict[str, Any]:
        """Open a scene in the editor.

        Args:
            path: Path to the scene file (e.g. "res://scenes/main.tscn")
        """
        return await bridge.call_godot("open_scene", {"path": path})

    @mcp.tool()
    async def delete_scene(path: str) -> dict[str, Any]:
        """Delete a scene file.

        Args:
            path: Path to the scene file to delete
        """
        return await bridge.call_godot("delete_scene", {"path": path})

    @mcp.tool()
    async def add_scene_instance(
        scene_path: str,
        parent_path: str = ".",
        name: str = "",
    ) -> dict[str, Any]:
        """Instance a scene as a child node.

        Args:
            scene_path: Path to the scene to instance (e.g. "res://scenes/enemy.tscn")
            parent_path: Path of the parent node (default "." for root)
            name: Optional name for the instanced node
        """
        return await bridge.call_godot("add_scene_instance", {
            "scene_path": scene_path,
            "parent_path": parent_path,
            "name": name,
        })

    @mcp.tool()
    async def play_scene(
        mode: str = "main",
        scene_path: str = "",
    ) -> dict[str, Any]:
        """Run a scene. Mode can be "main", "current", or "custom".

        Args:
            mode: Play mode - "main" (default), "current", or "custom"
            scene_path: Scene path (required if mode is "custom")
        """
        return await bridge.call_godot("play_scene", {
            "mode": mode,
            "scene_path": scene_path,
        })

    @mcp.tool()
    async def stop_scene() -> dict[str, Any]:
        """Stop the currently running scene."""
        return await bridge.call_godot("stop_scene")

    @mcp.tool()
    async def save_scene(path: str = "") -> dict[str, Any]:
        """Save the current scene to disk.

        Args:
            path: Optional path to save to (empty = save to current path)
        """
        return await bridge.call_godot("save_scene", {"path": path})

    @mcp.tool()
    async def get_scene_exports(path: str) -> dict[str, Any]:
        """Get exported variables from a scene's root script.

        Args:
            path: Path to the scene file (e.g. "res://scenes/player.tscn")
        """
        return await bridge.call_godot("get_scene_exports", {"path": path})
