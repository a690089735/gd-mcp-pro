"""Testing and QA tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def run_test_scenario(
        steps: list[dict[str, Any]],
        name: str = "",
    ) -> dict[str, Any]:
        """Run an automated test scenario with multiple steps.

        Args:
            steps: List of test step dictionaries (action, params, assertions)
            name: Optional name for the test scenario
        """
        return await bridge.call_godot("run_test_scenario", {
            "steps": steps,
            "name": name,
        })

    @mcp.tool()
    async def assert_node_state(
        node_path: str,
        assertions: dict[str, Any],
    ) -> dict[str, Any]:
        """Assert that a node's properties match expected values.

        Args:
            node_path: Path to the node to check
            assertions: Dictionary of property names and expected values
        """
        return await bridge.call_godot("assert_node_state", {
            "node_path": node_path,
            "assertions": assertions,
        })

    @mcp.tool()
    async def assert_screen_text(text: str) -> dict[str, Any]:
        """Check if specific text is visible on screen in the running game.

        Args:
            text: Text to search for on screen
        """
        return await bridge.call_godot("assert_screen_text", {"text": text})

    @mcp.tool()
    async def compare_screenshots(
        image_a: str,
        image_b: str,
        threshold: float = 0.95,
    ) -> dict[str, Any]:
        """Compare two screenshots for visual similarity.

        Args:
            image_a: Path or base64 of first image
            image_b: Path or base64 of second image
            threshold: Similarity threshold (0.0-1.0, default 0.95)
        """
        return await bridge.call_godot("compare_screenshots", {
            "image_a": image_a,
            "image_b": image_b,
            "threshold": threshold,
        })

    @mcp.tool()
    async def run_stress_test(
        duration: float = 5.0,
        actions: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Run a performance stress test.

        Args:
            duration: Test duration in seconds (default 5.0)
            actions: Optional list of actions to repeat during stress test
        """
        return await bridge.call_godot("run_stress_test", {
            "duration": duration,
            "actions": actions or [],
        })

    @mcp.tool()
    async def get_test_report() -> dict[str, Any]:
        """Get the results report from the last test run."""
        return await bridge.call_godot("get_test_report")