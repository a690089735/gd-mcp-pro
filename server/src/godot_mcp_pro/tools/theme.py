"""Theme and UI tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def create_theme(
        path: str,
        default_font_size: int = 0,
    ) -> dict[str, Any]:
        """Create a new Theme resource file (parent directories are created).

        Args:
            path: Where to save the theme (e.g. "res://themes/main.tres")
            default_font_size: Theme-wide default font size (0 = leave unset)
        """
        params: dict[str, Any] = {"path": path}
        if default_font_size > 0:
            params["default_font_size"] = default_font_size
        return await bridge.call_godot("create_theme", params)

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
    ) -> dict[str, Any]:
        """Set a theme constant override on a Control node.

        Adds a per-node override (add_theme_constant_override); theme types are
        not applicable here.

        Args:
            node_path: Path to the Control node
            name: Constant name (e.g. "margin_left")
            value: Integer value
        """
        return await bridge.call_godot("set_theme_constant", {
            "node_path": node_path,
            "name": name,
            "value": value,
        })

    @mcp.tool()
    async def set_theme_font_size(
        node_path: str,
        name: str,
        size: int,
    ) -> dict[str, Any]:
        """Set a theme font size override on a Control node.

        Adds a per-node override (add_theme_font_size_override); theme types are
        not applicable here.

        Args:
            node_path: Path to the Control node
            name: Font size name (e.g. "font_size")
            size: Font size in pixels
        """
        return await bridge.call_godot("set_theme_font_size", {
            "node_path": node_path,
            "name": name,
            "size": size,
        })

    @mcp.tool()
    async def set_theme_stylebox(
        node_path: str,
        name: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Set a StyleBoxFlat override on a Control node.

        Args:
            node_path: Path to the Control node
            name: StyleBox name (e.g. "panel", "normal")
            properties: Any of: bg_color (hex or "Color(r,g,b,a)"), border_color,
                border_width (int, all sides), corner_radius (int, all corners),
                padding (int, all sides)
        """
        return await bridge.call_godot("set_theme_stylebox", {
            **(properties or {}),
            "node_path": node_path,
            "name": name,
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
        grow_h: str = "",
        grow_v: str = "",
        margins: dict[str, int] | None = None,
        separation: int | None = None,
    ) -> dict[str, Any]:
        """Configure a Control node's layout and sizing.

        Args:
            node_path: Path to the Control node
            anchor_preset: Anchor preset (e.g. "full_rect", "center", "top_left")
            min_size_x: Minimum width (sent together with min_size_y)
            min_size_y: Minimum height (sent together with min_size_x)
            size_flags_h: Horizontal size flags ("fill", "expand", "fill_expand",
                "shrink_center", "shrink_end")
            size_flags_v: Vertical size flags, same values as size_flags_h
            grow_h: Horizontal grow direction ("begin", "end", "both")
            grow_v: Vertical grow direction ("begin", "end", "both")
            margins: MarginContainer margins {left, top, right, bottom}
                (ignored for other node types)
            separation: BoxContainer separation in px (ignored for other types)
        """
        params: dict[str, Any] = {"node_path": node_path}
        if anchor_preset:
            params["anchor_preset"] = anchor_preset
        if min_size_x is not None or min_size_y is not None:
            # GDScript parses this with Expression, so it must be a Vector2 literal.
            params["min_size"] = (
                f"Vector2({min_size_x or 0}, {min_size_y or 0})"
            )
        if size_flags_h:
            params["size_flags_h"] = size_flags_h
        if size_flags_v:
            params["size_flags_v"] = size_flags_v
        if grow_h:
            params["grow_h"] = grow_h
        if grow_v:
            params["grow_v"] = grow_v
        if margins:
            params["margins"] = margins
        if separation is not None:
            params["separation"] = separation
        return await bridge.call_godot("setup_control", params)
