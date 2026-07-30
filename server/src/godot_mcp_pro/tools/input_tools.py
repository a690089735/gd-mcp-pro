"""Input simulation and input map tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    # --- Input simulation tools ---

    @mcp.tool()
    async def simulate_key(
        keycode: str,
        pressed: bool = True,
        shift: bool = False,
        ctrl: bool = False,
        alt: bool = False,
    ) -> dict[str, Any]:
        """Simulate a keyboard key press/release in the running game.

        Args:
            keycode: Key code string (e.g. "space", "w", "escape")
            pressed: Whether the key is pressed (True) or released (False)
            shift: Whether Shift is held
            ctrl: Whether Ctrl is held
            alt: Whether Alt is held
        """
        return await bridge.call_godot("simulate_key", {
            "keycode": keycode,
            "pressed": pressed,
            "shift": shift,
            "ctrl": ctrl,
            "alt": alt,
        })

    @mcp.tool()
    async def simulate_mouse_click(
        x: float = 0,
        y: float = 0,
        button: int = 1,
        pressed: bool = True,
        double_click: bool = False,
        auto_release: bool = True,
    ) -> dict[str, Any]:
        """Simulate a mouse click at a position in the running game.

        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button (1=left, 2=right, 3=middle)
            pressed: Whether button is pressed (True) or released (False)
            double_click: Whether this is a double click
            auto_release: Send a matching release after the press (default True)
        """
        return await bridge.call_godot("simulate_mouse_click", {
            "x": x,
            "y": y,
            "button": button,
            "pressed": pressed,
            "double_click": double_click,
            "auto_release": auto_release,
        })

    @mcp.tool()
    async def simulate_mouse_move(
        x: float = 0,
        y: float = 0,
        relative_x: float = 0,
        relative_y: float = 0,
        button_mask: int = 0,
        unhandled: bool | None = None,
    ) -> dict[str, Any]:
        """Simulate mouse movement in the running game.

        Args:
            x: Target X position
            y: Target Y position
            relative_x: Relative X movement
            relative_y: Relative Y movement
            button_mask: Held mouse buttons as a bitmask (for drag motion)
            unhandled: Deliver as an unhandled input event instead of a normal one
        """
        params: dict[str, Any] = {
            "x": x,
            "y": y,
            "relative_x": relative_x,
            "relative_y": relative_y,
            "button_mask": button_mask,
        }
        if unhandled is not None:
            params["unhandled"] = unhandled
        return await bridge.call_godot("simulate_mouse_move", params)

    @mcp.tool()
    async def simulate_action(
        action: str,
        pressed: bool = True,
        strength: float = 1.0,
    ) -> dict[str, Any]:
        """Simulate a Godot Input Action in the running game.

        Args:
            action: Action name (e.g. "ui_accept", "move_left")
            pressed: Whether the action is pressed or released
            strength: Action strength (0.0 to 1.0)
        """
        return await bridge.call_godot("simulate_action", {
            "action": action,
            "pressed": pressed,
            "strength": strength,
        })

    @mcp.tool()
    async def simulate_sequence(
        events: list[dict[str, Any]],
        frame_delay: int = 0,
    ) -> dict[str, Any]:
        """Execute a sequence of input events with frame delays.

        Args:
            events: List of input event dictionaries, each with type, params, and optional delay_frames
            frame_delay: Default rendered frames to wait between events (0 = engine default)
        """
        params: dict[str, Any] = {"events": events}
        if frame_delay > 0:
            params["frame_delay"] = frame_delay
        return await bridge.call_godot("simulate_sequence", params)

    # --- Input map tools ---

    @mcp.tool()
    async def get_input_actions(
        filter: str = "",
        include_builtin: bool = False,
    ) -> dict[str, Any]:
        """List all defined input actions and their mappings.

        Args:
            filter: Only return actions whose name contains this substring
            include_builtin: Include Godot's built-in "ui_*" actions and the
                editor's own actions (default False = project actions only)
        """
        return await bridge.call_godot("get_input_actions", {
            "filter": filter,
            "include_builtin": include_builtin,
        })

    @mcp.tool()
    async def set_input_action(
        action: str,
        events: list[dict[str, Any]] | None = None,
        deadzone: float = 0.5,
    ) -> dict[str, Any]:
        """Create or modify an input action.

        Args:
            action: Action name to create or modify
            events: List of input event definitions
            deadzone: Dead zone for the action (default 0.5)
        """
        return await bridge.call_godot("set_input_action", {
            "action": action,
            "events": events or [],
            "deadzone": deadzone,
        })