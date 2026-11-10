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
        pivot_offset_ratio: dict[str, float] | None = None,
        max_size: dict[str, float] | None = None,
        offset_transform: dict[str, Any] | None = None,
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
            pivot_offset_ratio: Pivot as a ratio of the size {x, y}
                (Godot 4.6+, e.g. {"x": 0.5, "y": 0.5} = centre)
            max_size: Maximum size {x, y} (custom_maximum_size, Godot 4.7+)
            offset_transform: Visual offset transform (Godot 4.7+). Keys:
                position, position_ratio, scale, pivot, pivot_ratio ({x, y}
                each), rotation_degrees (number), visual_only, enabled (bool).
                Setting any value enables it unless enabled=false is given.
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
        if pivot_offset_ratio is not None:
            params["pivot_offset_ratio"] = pivot_offset_ratio
        if max_size is not None:
            params["max_size"] = max_size
        if offset_transform is not None:
            params["offset_transform"] = offset_transform
        return await bridge.call_godot("setup_control", params)

    @mcp.tool()
    async def add_virtual_joystick(
        parent_path: str = ".",
        name: str = "VirtualJoystick",
        mode: str = "fixed",
        visibility: str = "always",
        action_left: str = "ui_left",
        action_right: str = "ui_right",
        action_up: str = "ui_up",
        action_down: str = "ui_down",
        anchor_preset: str = "",
        margin: int = 0,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add an on-screen VirtualJoystick bound to four Input Map actions (Godot 4.7+).

        The joystick reacts to touch only; the response warns about missing
        actions and about emulate_touch_from_mouse being off. Undoable.

        Args:
            parent_path: Parent node path (default "." = scene root)
            name: Node name (default "VirtualJoystick")
            mode: "fixed", "dynamic" or "following"
            visibility: "always" or "when_touched"
            action_left: Input action for left (default "ui_left")
            action_right: Input action for right (default "ui_right")
            action_up: Input action for up (default "ui_up")
            action_down: Input action for down (default "ui_down")
            anchor_preset: Anchor preset, e.g. "bottom_left" (exclusive with
                properties.position)
            margin: Margin in px used with anchor_preset (default 0)
            properties: Any of: joystick_size (10-500), tip_size (5-250),
                deadzone_ratio (0-1), clampzone_ratio (0-2),
                initial_offset_ratio, size, position ({x, y} each)
        """
        params: dict[str, Any] = {
            **(properties or {}),
            "parent_path": parent_path,
            "name": name,
            "mode": mode,
            "visibility": visibility,
            "action_left": action_left,
            "action_right": action_right,
            "action_up": action_up,
            "action_down": action_down,
        }
        if anchor_preset:
            params["anchor_preset"] = anchor_preset
        if margin:
            params["margin"] = margin
        return await bridge.call_godot("add_virtual_joystick", params)
