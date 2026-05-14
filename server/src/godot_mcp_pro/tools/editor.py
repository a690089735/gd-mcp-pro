"""Editor control tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def get_editor_errors() -> dict[str, Any]:
        """Get current editor errors and stack traces."""
        return await bridge.call_godot("get_editor_errors")

    @mcp.tool()
    async def get_output_log(lines: int = 100) -> dict[str, Any]:
        """Get output panel content.

        Args:
            lines: Maximum number of lines to return (default 100)
        """
        return await bridge.call_godot("get_output_log", {"lines": lines})

    @mcp.tool()
    async def get_editor_screenshot(save_path: str = "") -> dict[str, Any]:
        """Capture a screenshot of the editor viewport.

        Args:
            save_path: Optional path to save the screenshot file
        """
        return await bridge.call_godot("get_editor_screenshot", {"save_path": save_path})

    @mcp.tool()
    async def get_game_screenshot(save_path: str = "") -> dict[str, Any]:
        """Capture a screenshot of the running game.

        Args:
            save_path: Optional path to save the screenshot file
        """
        return await bridge.call_godot("get_game_screenshot", {"save_path": save_path})

    @mcp.tool()
    async def execute_editor_script(code: str) -> dict[str, Any]:
        """Run arbitrary GDScript code in the editor context.

        Args:
            code: GDScript code to execute
        """
        return await bridge.call_godot("execute_editor_script", {"code": code})

    @mcp.tool()
    async def clear_output() -> dict[str, Any]:
        """Clear the output panel."""
        return await bridge.call_godot("clear_output")

    @mcp.tool()
    async def get_signals(node_path: str) -> dict[str, Any]:
        """Get all signals of a node with their connections.

        Args:
            node_path: Path to the node
        """
        return await bridge.call_godot("get_signals", {"node_path": node_path})

    @mcp.tool()
    async def reload_plugin() -> dict[str, Any]:
        """Reload the MCP plugin (auto-reconnects after reload)."""
        return await bridge.call_godot("reload_plugin")

    @mcp.tool()
    async def reload_project() -> dict[str, Any]:
        """Rescan filesystem and reload scripts."""
        return await bridge.call_godot("reload_project")

    @mcp.tool()
    async def set_auto_dismiss(enabled: bool = True) -> dict[str, Any]:
        """Enable or disable auto-dismissal of editor dialogs.

        Args:
            enabled: Whether to enable auto-dismiss (default True)
        """
        return await bridge.call_godot("set_auto_dismiss", {"enabled": enabled})

    @mcp.tool()
    async def get_editor_camera() -> dict[str, Any]:
        """Get the current 3D editor camera transform and properties."""
        return await bridge.call_godot("get_editor_camera")

    @mcp.tool()
    async def set_editor_camera(
        position: dict[str, float] | None = None,
        rotation: dict[str, float] | None = None,
        distance: float | None = None,
    ) -> dict[str, Any]:
        """Set the 3D editor camera transform.

        Args:
            position: Camera position {x, y, z}
            rotation: Camera rotation in degrees {x, y, z}
            distance: Distance from pivot point
        """
        params: dict[str, Any] = {}
        if position is not None:
            params["position"] = position
        if rotation is not None:
            params["rotation"] = rotation
        if distance is not None:
            params["distance"] = distance
        return await bridge.call_godot("set_editor_camera", params)
