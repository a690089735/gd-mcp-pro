"""Project management tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def get_project_info() -> dict[str, Any]:
        """Get project metadata including name, version, viewport size, and autoloads."""
        return await bridge.call_godot("get_project_info")

    @mcp.tool()
    async def get_filesystem_tree(
        path: str = "res://",
        filter: str = "",
        max_depth: int = 10,
    ) -> dict[str, Any]:
        """Get recursive file tree of the project.

        Args:
            path: Root path to start from (default "res://")
            filter: File extension filter (e.g. ".gd", ".tscn")
            max_depth: Maximum recursion depth (default 10)
        """
        return await bridge.call_godot("get_filesystem_tree", {
            "path": path,
            "filter": filter,
            "max_depth": max_depth,
        })

    @mcp.tool()
    async def search_files(
        query: str,
        path: str = "res://",
        file_type: str = "",
        max_results: int = 50,
    ) -> dict[str, Any]:
        """Fuzzy/glob file search in the project.

        Args:
            query: Search query (supports glob patterns)
            path: Directory to search in (default "res://")
            file_type: Filter by file extension (e.g. ".gd")
            max_results: Maximum number of results (default 50)
        """
        return await bridge.call_godot("search_files", {
            "query": query,
            "path": path,
            "file_type": file_type,
            "max_results": max_results,
        })

    @mcp.tool()
    async def search_in_files(
        query: str,
        path: str = "res://",
        max_results: int = 50,
        regex: bool = False,
        file_type: str = "",
    ) -> dict[str, Any]:
        """Search content inside project files.

        Args:
            query: Search string or regex pattern
            path: Directory to search in (default "res://")
            max_results: Maximum number of results (default 50)
            regex: Whether to treat query as regex (default False)
            file_type: Filter by file extension (e.g. ".gd")
        """
        return await bridge.call_godot("search_in_files", {
            "query": query,
            "path": path,
            "max_results": max_results,
            "regex": regex,
            "file_type": file_type,
        })

    @mcp.tool()
    async def get_project_settings(
        section: str = "",
        key: str = "",
    ) -> dict[str, Any]:
        """Read project.godot settings.

        Args:
            section: Settings section to filter (optional)
            key: Specific key to read (optional)
        """
        return await bridge.call_godot("get_project_settings", {
            "section": section,
            "key": key,
        })

    @mcp.tool()
    async def set_project_setting(key: str, value: Any) -> dict[str, Any]:
        """Set a project setting via editor API.

        Args:
            key: Setting key path (e.g. "application/config/name")
            value: Value to set
        """
        return await bridge.call_godot("set_project_setting", {
            "key": key,
            "value": value,
        })

    @mcp.tool()
    async def uid_to_project_path(uid: str) -> dict[str, Any]:
        """Convert a UID to a res:// project path.

        Args:
            uid: The UID string to convert
        """
        return await bridge.call_godot("uid_to_project_path", {"uid": uid})

    @mcp.tool()
    async def project_path_to_uid(path: str) -> dict[str, Any]:
        """Convert a res:// project path to its UID.

        Args:
            path: The res:// path to convert
        """
        return await bridge.call_godot("project_path_to_uid", {"path": path})