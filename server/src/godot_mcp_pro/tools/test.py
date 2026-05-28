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
        scene_path: str = "",
    ) -> dict[str, Any]:
        """Run an automated test scenario with multiple steps.

        Args:
            steps: List of test step dictionaries (action, params, assertions)
            name: Optional name for the test scenario
            scene_path: Optional scene to play before running steps ("main", "current", or a res:// path)
        """
        params: dict[str, Any] = {"steps": steps}
        if name:
            params["name"] = name
        if scene_path:
            params["scene_path"] = scene_path
        return await bridge.call_godot("run_test_scenario", params)

    @mcp.tool()
    async def assert_node_state(
        node_path: str,
        property: str,
        expected: Any,
        operator: str = "eq",
    ) -> dict[str, Any]:
        """Assert that a node's properties match expected values.

        Args:
            node_path: Path to the node to check
            property: Property name to assert (supports sub-properties like "position:y")
            expected: Expected value
            operator: Comparison operator (eq, neq, gt, lt, gte, lte, contains, type_is)
        """
        return await bridge.call_godot("assert_node_state", {
            "node_path": node_path,
            "property": property,
            "expected": expected,
            "operator": operator,
        })

    @mcp.tool()
    async def assert_screen_text(
        text: str,
        partial: bool = True,
        case_sensitive: bool = True,
    ) -> dict[str, Any]:
        """Check if specific text is visible on screen in the running game.

        Args:
            text: Text to search for on screen
            partial: Whether to match partial text (default True)
            case_sensitive: Whether the search is case-sensitive (default True)
        """
        return await bridge.call_godot("assert_screen_text", {
            "text": text,
            "partial": partial,
            "case_sensitive": case_sensitive,
        })

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