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
        loop_mode: int | None = None,
    ) -> dict[str, Any]:
        """Create a new animation in an AnimationPlayer.

        Args:
            node_path: Path to the AnimationPlayer node
            name: Name for the new animation
            length: Animation length in seconds (default 1.0)
            loop: Shorthand for loop_mode=1 (linear) when True
            loop_mode: Explicit loop mode: 0=none, 1=linear, 2=pingpong
        """
        mode = loop_mode if loop_mode is not None else (1 if loop else 0)
        return await bridge.call_godot("create_animation", {
            "node_path": node_path,
            "name": name,
            "length": length,
            "loop_mode": mode,
        })

    @mcp.tool()
    async def add_animation_track(
        node_path: str,
        animation: str,
        track_type: str,
        track_path: str,
        update_mode: str = "",
    ) -> dict[str, Any]:
        """Add a track to an animation (value/position/rotation/method/bezier).

        Args:
            node_path: Path to the AnimationPlayer node
            animation: Name of the animation
            track_type: One of "value" (default), "position_2d", "rotation_2d",
                "scale_2d", "method", "bezier", "blend_shape". The *_2d names map
                onto Godot's 3D transform track types, which it also uses for 2D.
                Any unrecognised value silently falls back to "value".
            track_path: Node path and property for the track (e.g. "Sprite2D:position")
            update_mode: Value-track update mode ("continuous", "discrete", "capture").
                Only applied to "value" tracks.
        """
        params: dict[str, Any] = {
            "node_path": node_path,
            "animation": animation,
            "track_type": track_type,
            "track_path": track_path,
        }
        if update_mode:
            params["update_mode"] = update_mode
        return await bridge.call_godot("add_animation_track", params)

    @mcp.tool()
    async def set_animation_keyframe(
        node_path: str,
        animation: str,
        track_index: int,
        time: float,
        value: Any,
        easing: float = 1.0,
    ) -> dict[str, Any]:
        """Insert a keyframe into an animation track.

        Args:
            node_path: Path to the AnimationPlayer node
            animation: Name of the animation
            track_index: Index of the track
            time: Time position in seconds
            value: Keyframe value (auto-parsed for Vector2, Color, etc.)
            easing: Transition/easing curve for the key (default 1.0 = linear)
        """
        return await bridge.call_godot("set_animation_keyframe", {
            "node_path": node_path,
            "animation": animation,
            "track_index": track_index,
            "time": time,
            "value": value,
            "easing": easing,
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
            "name": animation,
        })

    # --- AnimationTree tools ---

    @mcp.tool()
    async def create_animation_tree(
        node_path: str,
        anim_player: str = "",
        name: str = "AnimationTree",
    ) -> dict[str, Any]:
        """Create an AnimationTree (root is an AnimationNodeStateMachine).

        Args:
            node_path: Path of the node the AnimationTree is added to
            anim_player: Path to the AnimationPlayer to drive
                (empty = auto-detect a sibling/child AnimationPlayer)
            name: Name for the new AnimationTree node (default "AnimationTree")
        """
        params: dict[str, Any] = {"node_path": node_path, "name": name}
        if anim_player:
            params["anim_player"] = anim_player
        return await bridge.call_godot("create_animation_tree", params)

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
        state_type: str = "animation",
        position_x: float = 0.0,
        position_y: float = 0.0,
    ) -> dict[str, Any]:
        """Add a state to an AnimationTree state machine.

        Args:
            node_path: Path to the AnimationTree node
            state_name: Name for the new state
            animation: Animation name to play in this state
            state_machine_path: Path to the state machine node (empty for root)
            state_type: State node type (default "animation";
                also "state_machine" / "blend_tree" for nested graphs)
            position_x: X position in the state machine graph
            position_y: Y position in the state machine graph
        """
        return await bridge.call_godot("add_state_machine_state", {
            "node_path": node_path,
            "state_name": state_name,
            "animation": animation,
            "state_machine_path": state_machine_path,
            "state_type": state_type,
            "position_x": position_x,
            "position_y": position_y,
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
        advance_expression: str = "",
        auto_advance: bool = False,
        switch_mode: str = "immediate",
        xfade_time: float | None = None,
        state_machine_path: str = "",
    ) -> dict[str, Any]:
        """Add a transition between states in an AnimationTree state machine.

        Args:
            node_path: Path to the AnimationTree node
            from_state: Source state name
            to_state: Destination state name
            advance_expression: Expression that must evaluate true to advance
            auto_advance: Set advance_mode to "auto" (default False = "enabled")
            switch_mode: "immediate", "sync", or "at_end" (default "immediate")
            xfade_time: Cross-fade duration in seconds
            state_machine_path: Path to the state machine node (empty for root)
        """
        params: dict[str, Any] = {
            "node_path": node_path,
            "from_state": from_state,
            "to_state": to_state,
            "switch_mode": switch_mode,
            "advance_mode": "auto" if auto_advance else "enabled",
            "state_machine_path": state_machine_path,
        }
        if advance_expression:
            params["advance_expression"] = advance_expression
        if xfade_time is not None:
            params["xfade_time"] = xfade_time
        return await bridge.call_godot("add_state_machine_transition", params)

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
        blend_tree_state: str,
        blend_node_name: str,
        blend_node_type: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create or replace a node inside an AnimationTree blend tree.

        Args:
            node_path: Path to the AnimationTree node
            blend_tree_state: Name of the state machine state holding the blend
                tree (use the root blend tree's state name)
            blend_node_name: Name for the blend node
            blend_node_type: Blend node class suffix (case-sensitive):
                "Animation", "Add2", "Add3", "Sub2", "Blend2", "Blend3",
                "TimeScale", "TimeSeek", "Transition", "OneShot"
            properties: Any of: animation (str, for "Animation" nodes),
                position_x / position_y (float, graph layout),
                state_machine_path (str, for nested state machines),
                connect_to (str, blend node to wire this node's output into),
                connect_port (int, input port on connect_to, default 0)
        """
        return await bridge.call_godot("set_blend_tree_node", {
            **(properties or {}),
            "node_path": node_path,
            "blend_tree_state": blend_tree_state,
            "bt_node_name": blend_node_name,
            "bt_node_type": blend_node_type,
        })
