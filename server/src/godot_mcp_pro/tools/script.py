"""Script management tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def list_scripts(
        path: str = "res://",
        recursive: bool = True,
    ) -> dict[str, Any]:
        """List all scripts in the project with class info.

        Args:
            path: Directory to search (default "res://")
            recursive: Whether to search recursively (default True)
        """
        return await bridge.call_godot("list_scripts", {
            "path": path,
            "recursive": recursive,
        })

    @mcp.tool()
    async def read_script(path: str) -> dict[str, Any]:
        """Read the content of a script file.

        Args:
            path: Path to the script (e.g. "res://scripts/player.gd")
        """
        return await bridge.call_godot("read_script", {"path": path})

    @mcp.tool()
    async def create_script(
        path: str,
        content: str = "",
        extends: str = "",
        class_name: str = "",
    ) -> dict[str, Any]:
        """Create a new script file with optional content or auto-generated template.

        Args:
            path: Where to save the script (e.g. "res://scripts/enemy.gd")
            content: Full script content (if empty, generates template)
            extends: Base class to extend (e.g. "CharacterBody2D")
            class_name: Optional class_name declaration
        """
        return await bridge.call_godot("create_script", {
            "path": path,
            "content": content,
            "extends": extends,
            "class_name": class_name,
        })

    @mcp.tool()
    async def edit_script(
        path: str,
        content: str = "",
        search: str = "",
        replace: str = "",
        regex: bool = False,
        line: int = -1,
        insert: str = "",
    ) -> dict[str, Any]:
        """Edit an existing script via search-and-replace, full replacement, or line insert.

        Args:
            path: Path to the script to edit
            content: Full replacement content (replaces entire file)
            search: Text to search for (used with replace)
            replace: Replacement text (used with search)
            regex: Whether search is a regex pattern (default False)
            line: Line number for insertion (-1 = disabled)
            insert: Text to insert at the specified line
        """
        return await bridge.call_godot("edit_script", {
            "path": path,
            "content": content,
            "search": search,
            "replace": replace,
            "regex": regex,
            "line": line,
            "insert": insert,
        })

    @mcp.tool()
    async def attach_script(
        node_path: str,
        script_path: str,
    ) -> dict[str, Any]:
        """Attach a script to a node.

        Args:
            node_path: Path to the node
            script_path: Path to the script file (e.g. "res://scripts/player.gd")
        """
        return await bridge.call_godot("attach_script", {
            "node_path": node_path,
            "script_path": script_path,
        })

    @mcp.tool()
    async def get_open_scripts() -> dict[str, Any]:
        """Get list of scripts currently open in the editor."""
        return await bridge.call_godot("get_open_scripts")

    @mcp.tool()
    async def validate_script(path: str) -> dict[str, Any]:
        """Validate GDScript syntax without running it.

        Args:
            path: Path to the script to validate
        """
        return await bridge.call_godot("validate_script", {"path": path})

