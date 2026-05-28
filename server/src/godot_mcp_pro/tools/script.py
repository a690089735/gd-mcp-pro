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
        force: bool = False,
    ) -> dict[str, Any]:
        """Create a new script file with optional content or auto-generated template.

        Args:
            path: Where to save the script (e.g. "res://scripts/enemy.gd")
            content: Full script content (if empty, generates template)
            extends: Base class to extend (e.g. "CharacterBody2D")
            class_name: Optional class_name declaration
            force: Force write even if the file is open in the editor (default False)
        """
        params: dict[str, Any] = {
            "path": path,
            "content": content,
            "extends": extends,
            "class_name": class_name,
        }
        if force:
            params["force"] = True
        return await bridge.call_godot("create_script", params)

    @mcp.tool()
    async def edit_script(
        path: str,
        content: str = "",
        search: str = "",
        replace: str = "",
        regex: bool = False,
        line: int = -1,
        insert: str = "",
        start_line: int = -1,
        end_line: int = -1,
        force: bool = False,
    ) -> dict[str, Any]:
        """Edit an existing script via search-and-replace, full replacement, line range replacement, or line insert.

        Args:
            path: Path to the script to edit
            content: Full replacement content (replaces entire file), or replacement text for line range mode
            search: Text to search for (used with replace)
            replace: Replacement text (used with search)
            regex: Whether search is a regex pattern (default False)
            line: Line number for insertion (-1 = disabled)
            insert: Text to insert at the specified line
            start_line: Start line for range replacement (1-based inclusive, -1 = disabled)
            end_line: End line for range replacement (1-based inclusive, -1 = disabled)
            force: Force write even if the file is open in the editor (default False)
        """
        params: dict[str, Any] = {"path": path}
        if force:
            params["force"] = True

        # Determine edit mode and only send relevant params
        if search:
            # Search-and-replace mode → wrap into replacements array
            params["replacements"] = [{"search": search, "replace": replace, "regex": regex}]
        elif content and (start_line > 0 or end_line > 0):
            # Line range replacement mode
            params["content"] = content
            if start_line > 0:
                params["start_line"] = start_line
            if end_line > 0:
                params["end_line"] = end_line
        elif content:
            # Full content replacement mode
            params["content"] = content
        elif line >= 0 and insert:
            # Line insertion mode (map to GDScript param names)
            params["insert_at_line"] = line
            params["text"] = insert

        return await bridge.call_godot("edit_script", params)

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