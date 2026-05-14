"""Runtime inspection and control tools for running games."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def get_game_scene_tree(max_depth: int = -1) -> dict[str, Any]:
        """Get the scene tree of the running game.

        Args:
            max_depth: Maximum depth to traverse (-1 for unlimited)
        """
        return await bridge.call_godot("get_game_scene_tree", {"max_depth": max_depth})

    @mcp.tool()
    async def get_game_node_properties(node_path: str) -> dict[str, Any]:
        """Get properties of a node in the running game.

        Args:
            node_path: Path to the node in the game scene tree
        """
        return await bridge.call_godot("get_game_node_properties", {"node_path": node_path})

    @mcp.tool()
    async def set_game_node_property(
        node_path: str,
        property: str,
        value: Any,
    ) -> dict[str, Any]:
        """Set a property on a node in the running game.

        Args:
            node_path: Path to the node in the game scene tree
            property: Property name to set
            value: Value to set
        """
        return await bridge.call_godot("set_game_node_property", {
            "node_path": node_path,
            "property": property,
            "value": value,
        })

    @mcp.tool()
    async def execute_game_script(code: str) -> dict[str, Any]:
        """Run GDScript code in the game context.

        Args:
            code: GDScript code to execute in the running game
        """
        return await bridge.call_godot("execute_game_script", {"code": code})

    @mcp.tool()
    async def capture_frames(
        count: int = 1,
        interval: float = 0.5,
        save_path: str = "",
    ) -> dict[str, Any]:
        """Capture multiple screenshot frames from the running game.

        Args:
            count: Number of frames to capture (default 1)
            interval: Time between captures in seconds (default 0.5)
            save_path: Optional path to save screenshots
        """
        return await bridge.call_godot("capture_frames", {
            "count": count,
            "interval": interval,
            "save_path": save_path,
        })

    @mcp.tool()
    async def monitor_properties(
        node_path: str,
        properties: list[str],
        duration: float = 1.0,
        interval: float = 0.1,
    ) -> dict[str, Any]:
        """Record property values over time in the running game.

        Args:
            node_path: Path to the node to monitor
            properties: List of property names to monitor
            duration: How long to monitor in seconds (default 1.0)
            interval: Sample interval in seconds (default 0.1)
        """
        return await bridge.call_godot("monitor_properties", {
            "node_path": node_path,
            "properties": properties,
            "duration": duration,
            "interval": interval,
        })

    @mcp.tool()
    async def start_recording(name: str = "") -> dict[str, Any]:
        """Start recording input events in the running game.

        Args:
            name: Optional name for the recording
        """
        return await bridge.call_godot("start_recording", {"name": name})

    @mcp.tool()
    async def stop_recording() -> dict[str, Any]:
        """Stop the current input recording."""
        return await bridge.call_godot("stop_recording")

    @mcp.tool()
    async def replay_recording(name: str = "") -> dict[str, Any]:
        """Replay a previously recorded input sequence.

        Args:
            name: Name of the recording to replay (empty = last recording)
        """
        return await bridge.call_godot("replay_recording", {"name": name})

    @mcp.tool()
    async def find_nodes_by_script(script_path: str) -> dict[str, Any]:
        """Find nodes in the running game by their attached script.

        Args:
            script_path: Path to the script (e.g. "res://scripts/player.gd")
        """
        return await bridge.call_godot("find_nodes_by_script", {"script_path": script_path})

    @mcp.tool()
    async def get_autoload(name: str) -> dict[str, Any]:
        """Get properties of an autoload singleton node.

        Args:
            name: Autoload name (e.g. "GameManager")
        """
        return await bridge.call_godot("get_autoload", {"name": name})

    @mcp.tool()
    async def batch_get_properties(
        requests: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Batch get properties from multiple nodes in the running game.

        Args:
            requests: List of {node_path, properties} dictionaries
        """
        return await bridge.call_godot("batch_get_properties", {"requests": requests})

    @mcp.tool()
    async def find_ui_elements(
        root_path: str = "",
        type_filter: str = "",
    ) -> dict[str, Any]:
        """Find UI elements in the running game.

        Args:
            root_path: Root node path to search from (empty = scene root)
            type_filter: Filter by Control type (e.g. "Button")
        """
        return await bridge.call_godot("find_ui_elements", {
            "root_path": root_path,
            "type_filter": type_filter,
        })

    @mcp.tool()
    async def click_button_by_text(text: str) -> dict[str, Any]:
        """Click a button in the running game by its text content.

        Args:
            text: Button text to search for and click
        """
        return await bridge.call_godot("click_button_by_text", {"text": text})

    @mcp.tool()
    async def wait_for_node(
        node_path: str,
        timeout: float = 5.0,
    ) -> dict[str, Any]:
        """Wait for a node to appear in the running game scene tree.

        Args:
            node_path: Path of the node to wait for
            timeout: Maximum time to wait in seconds (default 5.0)
        """
        return await bridge.call_godot("wait_for_node", {
            "node_path": node_path,
            "timeout": timeout,
        })

    @mcp.tool()
    async def find_nearby_nodes(
        position_x: float,
        position_y: float,
        radius: float = 100.0,
        type_filter: str = "",
    ) -> dict[str, Any]:
        """Find nodes near a position in the running game.

        Args:
            position_x: X coordinate to search around
            position_y: Y coordinate to search around
            radius: Search radius (default 100.0)
            type_filter: Optional node type filter
        """
        return await bridge.call_godot("find_nearby_nodes", {
            "position_x": position_x,
            "position_y": position_y,
            "radius": radius,
            "type_filter": type_filter,
        })

    @mcp.tool()
    async def navigate_to(
        node_path: str,
        target_x: float,
        target_y: float,
    ) -> dict[str, Any]:
        """Navigate a node to a target position using pathfinding.

        Args:
            node_path: Path to the node to navigate
            target_x: Target X position
            target_y: Target Y position
        """
        return await bridge.call_godot("navigate_to", {
            "node_path": node_path,
            "target_x": target_x,
            "target_y": target_y,
        })

    @mcp.tool()
    async def move_to(
        node_path: str,
        target_x: float,
        target_y: float,
        speed: float = 100.0,
    ) -> dict[str, Any]:
        """Walk a character to a target position.

        Args:
            node_path: Path to the character node
            target_x: Target X position
            target_y: Target Y position
            speed: Movement speed (default 100.0)
        """
        return await bridge.call_godot("move_to", {
            "node_path": node_path,
            "target_x": target_x,
            "target_y": target_y,
            "speed": speed,
        })

    @mcp.tool()
    async def watch_signals(
        node_paths: list[str],
        signal_filter: list[str] | None = None,
        duration_ms: int = 5000,
    ) -> dict[str, Any]:
        """Watch for signal emissions on specified nodes in the running game.

        Args:
            node_paths: List of node paths to monitor
            signal_filter: Optional list of signal names to filter (empty = all signals)
            duration_ms: How long to watch in milliseconds (default 5000)
        """
        params: dict[str, Any] = {
            "node_paths": node_paths,
            "duration_ms": duration_ms,
        }
        if signal_filter is not None:
            params["signal_filter"] = signal_filter
        return await bridge.call_godot("watch_signals", params)
