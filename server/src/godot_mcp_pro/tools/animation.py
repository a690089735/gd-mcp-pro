"""Animation and AnimationTree tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    # --- Animation tools ---

    @mcp.tool()
    async def list_animations(node_path: str) -> dict[str, Any]:
        """List all animations in an AnimationPlayer.

        Args:
            node_path: Path to the AnimationPlayer node
        """
        return await bridge.call_godot("list_animations", {"node_path": node_path})

    @mcp.tool()
    async def create_animation(
        node_path: str,
        name: str,
        length: float = 1.0,
        loop: bool = False,
    ) -> dict[str, Any]:
        """Create a new animation in an AnimationPlayer.

        Args:
            node_path: Path to the AnimationPlayer node
            name: Name for the new animation
            length: Animation length in seconds (default 1.0)
            loop: Whether the animation should loop (default False)
        """
        return await bridge.call_godot("create_animation", {
            "node_path": node_path,
            "name": name,
            "length": length,
            "loop": loop,
        })

    @mcp.tool()
    async def add_animation_track(
        node_path: str,
        animation: str,
        track_type: str,
        track_path: str,
    ) -> dict[str, Any]:
        """Add a track to an animation (value/position/rotation/method/bezier).

        Args:
            node_path: Path to the AnimationPlayer node
            animation: Name of the animation
            track_type: Track type ("value", "position_3d", "rotation_3d", "method", "bezier")
            track_path: Node path and property for the track (e.g. "Sprite2D:position")
        """
        return await bridge.call_godot("add_animation_track", {
            "node_path": node_path,
            "animation": animation,
            "track_type": track_type,
            "track_path": track_path,
        })

    @mcp.tool()
    async def set_animation_keyframe(
        node_path: str,
        animation: str,
        track_index: int,
        time: float,
        value: Any,
    ) -> dict[str, Any]:
        """Insert a keyframe into an animation track.

        Args:
            node_path: Path to the AnimationPlayer node
            animation: Name of the animation
            track_index: Index of the track
            time: Time position in seconds
            value: Keyframe value (auto-parsed for Vector2, Color, etc.)
        """
        return await bridge.call_godot("set_animation_keyframe", {
            "node_path": node_path,
            "animation": animation,
            "track_index": track_index,
            "time": time,
            "value": value,
        })

    @mcp.tool()
    async def get_animation_info(
        node_path: str,
        animation: str,
    ) -> dict[str, Any]:
        """Get detailed animation info with all tracks and keyframes.

        Args:
            node_path: Path to the AnimationPlayer node
            animation: Name of the animation
        """
        return await bridge.call_godot("get_animation_info", {
            "node_path": node_path,
            "animation": animation,
        })

    @mcp.tool()
    async def remove_animation(
        node_path: str,
        animation: str,
    ) -> dict[str, Any]:
        """Remove an animation from an AnimationPlayer.

        Args:
            node_path: Path to the AnimationPlayer node
            animation: Name of the animation to remove
        """
        return await bridge.call_godot("remove_animation", {
            "node_path": node_path,
            "animation": animation,
        })

    # --- AnimationTree tools ---

    @mcp.tool()
    async def create_animation_tree(
        node_path: str,
        root_type: str = "state_machine",
    ) -> dict[str, Any]:
        """Create an AnimationTree with a root node type.

        Args:
            node_path: Path to attach the AnimationTree to
            root_type: Root type ("state_machine", "blend_tree", "blend_space_1d", "blend_space_2d")
        """
        return await bridge.call_godot("create_animation_tree", {
            "node_path": node_path,
            "root_type": root_type,
        })

    @mcp.tool()
    async def get_animation_tree_structure(node_path: str) -> dict[str, Any]:
        """Get the structure of an AnimationTree.

        Args:
            node_path: Path to the AnimationTree node
        """
        return await bridge.call_godot("get_animation_tree_structure", {"node_path": node_path})

    @mcp.tool()
    async def set_tree_parameter(
        node_path: str,
        parameter: str,
        value: Any,
    ) -> dict[str, Any]:
        """Set a parameter on an AnimationTree.

        Args:
            node_path: Path to the AnimationTree node
            parameter: Parameter path (e.g. "parameters/blend_amount")
            value: Value to set
        """
        return await bridge.call_godot("set_tree_parameter", {
            "node_path": node_path,
            "parameter": parameter,
            "value": value,
        })

    @mcp.tool()
    async def add_state_machine_state(
        node_path: str,
        state_name: str,
        animation: str = "",
        state_machine_path: str = "",
    ) -> dict[str, Any]:
        """Add a state to an AnimationTree state machine.

        Args:
            node_path: Path to the AnimationTree node
            state_name: Name for the new state
            animation: Animation name to play in this state
            state_machine_path: Path to the state machine node (empty for root)
        """
        return await bridge.call_godot("add_state_machine_state", {
            "node_path": node_path,
            "state_name": state_name,
            "animation": animation,
            "state_machine_path": state_machine_path,
        })

    @mcp.tool()
    async def remove_state_machine_state(
        node_path: str,
        state_name: str,
        state_machine_path: str = "",
    ) -> dict[str, Any]:
        """Remove a state from an AnimationTree state machine.

        Args:
            node_path: Path to the AnimationTree node
            state_name: Name of the state to remove
            state_machine_path: Path to the state machine node (empty for root)
        """
        return await bridge.call_godot("remove_state_machine_state", {
            "node_path": node_path,
            "state_name": state_name,
            "state_machine_path": state_machine_path,
        })

    @mcp.tool()
    async def add_state_machine_transition(
        node_path: str,
        from_state: str,
        to_state: str,
        advance_condition: str = "",
        auto_advance: bool = False,
        state_machine_path: str = "",
    ) -> dict[str, Any]:
        """Add a transition between states in an AnimationTree state machine.

        Args:
            node_path: Path to the AnimationTree node
            from_state: Source state name
            to_state: Destination state name
            advance_condition: Condition for automatic transition
            auto_advance: Whether to auto-advance (default False)
            state_machine_path: Path to the state machine node (empty for root)
        """
        return await bridge.call_godot("add_state_machine_transition", {
            "node_path": node_path,
            "from_state": from_state,
            "to_state": to_state,
            "advance_condition": advance_condition,
            "auto_advance": auto_advance,
            "state_machine_path": state_machine_path,
        })

    @mcp.tool()
    async def remove_state_machine_transition(
        node_path: str,
        from_state: str,
        to_state: str,
        state_machine_path: str = "",
    ) -> dict[str, Any]:
        """Remove a transition between states in an AnimationTree state machine.

        Args:
            node_path: Path to the AnimationTree node
            from_state: Source state name
            to_state: Destination state name
            state_machine_path: Path to the state machine node (empty for root)
        """
        return await bridge.call_godot("remove_state_machine_transition", {
            "node_path": node_path,
            "from_state": from_state,
            "to_state": to_state,
            "state_machine_path": state_machine_path,
        })

    @mcp.tool()
    async def set_blend_tree_node(
        node_path: str,
        blend_node_name: str,
        blend_node_type: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure a blend tree node in an AnimationTree.

        Args:
            node_path: Path to the AnimationTree node
            blend_node_name: Name of the blend node
            blend_node_type: Type of blend node
            properties: Optional properties to set on the blend node
        """
        return await bridge.call_godot("set_blend_tree_node", {
            "node_path": node_path,
            "blend_node_name": blend_node_name,
            "blend_node_type": blend_node_type,
            "properties": properties or {},
        })