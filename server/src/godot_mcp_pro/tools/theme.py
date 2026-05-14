"""Theme and UI tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def create_theme(
        path: str,
        base_type: str = "",
    ) -> dict[str, Any]:
        """Create a new Theme resource file.

        Args:
            path: Where to save the theme (e.g. "res://themes/main.tres")
            base_type: Base control type for theme defaults
        """
        return await bridge.call_godot("create_theme", {
            "path": path,
            "base_type": base_type,
        })

    @mcp.tool()
    async def set_theme_color(
        node_path: str,
        name: str,
        color: str,
        theme_type: str = "",
    ) -> dict[str, Any]:
        """Set a theme color override on a Control node.

        Args:
            node_path: Path to the Control node
            name: Color name (e.g. "font_color")
            color: Color value (hex "#ff0000" or "Color(1,0,0)")
            theme_type: Theme type override (optional)
        """
        return await bridge.call_godot("set_theme_color", {
            "node_path": node_path,
            "name": name,
            "color": color,
            "theme_type": theme_type,
        })

    @mcp.tool()
    async def set_theme_constant(
        node_path: str,
        name: str,
        value: int,
        theme_type: str = "",
    ) -> dict[str, Any]:
        """Set a theme constant override on a Control node.

        Args:
            node_path: Path to the Control node
            name: Constant name (e.g. "margin_left")
            value: Integer value
            theme_type: Theme type override (optional)
        """
        return await bridge.call_godot("set_theme_constant", {
            "node_path": node_path,
            "name": name,
            "value": value,
            "theme_type": theme_type,
        })

    @mcp.tool()
    async def set_theme_font_size(
        node_path: str,
        name: str,
        size: int,
        theme_type: str = "",
    ) -> dict[str, Any]:
        """Set a theme font size override on a Control node.

        Args:
            node_path: Path to the Control node
            name: Font size name (e.g. "font_size")
            size: Font size in pixels
            theme_type: Theme type override (optional)
        """
        return await bridge.call_godot("set_theme_font_size", {
            "node_path": node_path,
            "name": name,
            "size": size,
            "theme_type": theme_type,
        })

    @mcp.tool()
    async def set_theme_stylebox(
        node_path: str,
        name: str,
        properties: dict[str, Any] | None = None,
        theme_type: str = "",
    ) -> dict[str, Any]:
        """Set a StyleBoxFlat override on a Control node.

        Args:
            node_path: Path to the Control node
            name: StyleBox name (e.g. "panel", "normal")
            properties: StyleBoxFlat properties (bg_color, border_width, corner_radius, etc.)
            theme_type: Theme type override (optional)
        """
        return await bridge.call_godot("set_theme_stylebox", {
            "node_path": node_path,
            "name": name,
            "properties": properties or {},
            "theme_type": theme_type,
        })

    @mcp.tool()
    async def get_theme_info(node_path: str) -> dict[str, Any]:
        """Get theme overrides info for a Control node.

        Args:
            node_path: Path to the Control node
        """
        return await bridge.call_godot("get_theme_info", {"node_path": node_path})

    @mcp.tool()
    async def setup_control(
        node_path: str,
        anchor_preset: str = "",
        min_size_x: float | None = None,
        min_size_y: float | None = None,
        size_flags_h: str = "",
        size_flags_v: str = "",
        theme_path: str = "",
    ) -> dict[str, Any]:
        """Configure a Control node's layout, sizing, and theme.

        Args:
            node_path: Path to the Control node
            anchor_preset: Anchor preset (e.g. "full_rect", "center", "top_left")
            min_size_x: Minimum width
            min_size_y: Minimum height
            size_flags_h: Horizontal size flags ("fill", "expand", "shrink_center", etc.)
            size_flags_v: Vertical size flags
            theme_path: Path to a Theme resource to assign
        """
        params: dict[str, Any] = {"node_path": node_path}
        if anchor_preset:
            params["anchor_preset"] = anchor_preset
        if min_size_x is not None:
            params["min_size_x"] = min_size_x
        if min_size_y is not None:
            params["min_size_y"] = min_size_y
        if size_flags_h:
            params["size_flags_h"] = size_flags_h
        if size_flags_v:
            params["size_flags_v"] = size_flags_v
        if theme_path:
            params["theme_path"] = theme_path
        return await bridge.call_godot("setup_control", params)
