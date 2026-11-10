"""Headless execution tools.

Run scenes or scripts in a separate headless Godot process and retrieve
stdout/stderr, exit code and duration. This reaches a project's CLI test
suite, which editor-driven tools cannot see.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge
from ..timeouts import call_timeout


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def run_headless_scene(
        scene_path: str,
        timeout_sec: float = 120.0,
        quit_after_frames: int = -1,
        args: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run a scene in a separate headless Godot process and return its output.

        The child runs with --headless --path <project> <scene_path>.
        Useful for running a project's own CLI test suite that the editor cannot see.

        Args:
            scene_path: res:// path to the scene to run
            timeout_sec: Maximum seconds to wait (default 120, max 900)
            quit_after_frames: If >= 0, inject --quit-after <N> so Godot exits
                after N idle frames (useful for scenes without self-quit logic)
            args: Additional command-line arguments passed to the child Godot process
        """
        params: dict[str, Any] = {"scene_path": scene_path}
        if timeout_sec != 120.0:
            params["timeout_sec"] = timeout_sec
        if quit_after_frames >= 0:
            params["quit_after_frames"] = quit_after_frames
        if args:
            params["args"] = args
        return await bridge.call_godot(
            "run_headless_scene", params, timeout=call_timeout("run_headless_scene", params)
        )

    @mcp.tool()
    async def run_headless_script(
        script_path: str,
        timeout_sec: float = 120.0,
        quit_after_frames: int = -1,
        args: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run an `extends SceneTree` script in a separate headless Godot process.

        The child runs with --headless --path <project> --script <script_path>.
        Useful for running GDScript CLI tools or test scripts.

        Args:
            script_path: res:// path to the script (must extend SceneTree)
            timeout_sec: Maximum seconds to wait (default 120, max 900)
            quit_after_frames: If >= 0, inject --quit-after <N>
            args: Additional command-line arguments passed to the child Godot process
        """
        params: dict[str, Any] = {"script_path": script_path}
        if timeout_sec != 120.0:
            params["timeout_sec"] = timeout_sec
        if quit_after_frames >= 0:
            params["quit_after_frames"] = quit_after_frames
        if args:
            params["args"] = args
        return await bridge.call_godot(
            "run_headless_script", params, timeout=call_timeout("run_headless_script", params)
        )

    @mcp.tool()
    async def get_godot_executable() -> dict[str, Any]:
        """Get the path to the running Godot executable and project directory.

        Returns the executable path, project path, and platform name.
        Useful for constructing custom CLI invocations.
        """
        return await bridge.call_godot("get_godot_executable")
