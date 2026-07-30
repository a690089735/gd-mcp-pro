"""Batch operations and refactoring tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def find_nodes_by_type(
        type: str,
        recursive: bool = True,
    ) -> dict[str, Any]:
        """Find all nodes of a specific type in the current scene.

        Args:
            type: Node type to search for (e.g. "Sprite2D", "CollisionShape2D")
            recursive: Whether to search recursively (default True)
        """
        return await bridge.call_godot("find_nodes_by_type", {
            "type": type,
            "recursive": recursive,
        })

    @mcp.tool()
    async def find_signal_connections(
        node_path: str = "",
        signal_name: str = "",
    ) -> dict[str, Any]:
        """Find all signal connections in the current scene.

        Args:
            node_path: Root node to start from (empty = scene root)
            signal_name: Only return connections for this signal
        """
        params: dict[str, Any] = {"node_path": node_path}
        if signal_name:
            params["signal_name"] = signal_name
        return await bridge.call_godot("find_signal_connections", params)

    @mcp.tool()
    async def batch_set_property(
        type: str,
        property: str,
        value: Any,
    ) -> dict[str, Any]:
        """Set a property on all nodes of a specific type.

        Always walks the whole edited scene from its root.

        Args:
            type: Node type to target (e.g. "Sprite2D")
            property: Property name to set
            value: Value to set (supports smart type parsing)
        """
        return await bridge.call_godot("batch_set_property", {
            "type": type,
            "property": property,
            "value": value,
        })

    @mcp.tool()
    async def find_node_references(pattern: str) -> dict[str, Any]:
        """Search project files for a pattern (e.g. node name or path).

        Always searches the whole project from res:// (max 100 matches).
        Use find_script_references for a scoped search with more options.

        Args:
            pattern: Search pattern
        """
        return await bridge.call_godot("find_node_references", {"pattern": pattern})

    @mcp.tool()
    async def get_scene_dependencies(path: str = "") -> dict[str, Any]:
        """Get resource dependencies of a scene.

        Args:
            path: Scene path (empty = current scene)
        """
        return await bridge.call_godot("get_scene_dependencies", {"path": path})

    @mcp.tool()
    async def cross_scene_set_property(
        type: str,
        property: str,
        value: Any,
        scene_paths: list[str] | None = None,
        force: bool = False,
        dry_run: bool | None = None,
    ) -> dict[str, Any]:
        """Set a property across all scenes on nodes of a specific type.

        By default this performs a dry-run preview. Pass force=True to actually write changes.

        Args:
            type: Node type to target
            property: Property name to set
            value: Value to set
            scene_paths: List of scene paths (empty = all scenes)
            force: Must be True to actually write changes (default False = dry-run)
            dry_run: Explicit dry-run control (defaults to not force)
        """
        params: dict[str, Any] = {
            "type": type,
            "property": property,
            "value": value,
            "scene_paths": scene_paths or [],
        }
        if force:
            params["force"] = True
        if dry_run is not None:
            params["dry_run"] = dry_run
        return await bridge.call_godot("cross_scene_set_property", params)

    @mcp.tool()
    async def find_script_references(
        query: str,
        path: str = "res://",
        include_addons: bool = False,
    ) -> dict[str, Any]:
        """Find where a script or resource is used across the project.

        Scans .tscn/.gd/.tres/.cfg/.godot files line by line for `query`.

        Args:
            query: Text to search for (e.g. "res://scripts/player.gd" or a class name)
            path: Directory to search in (default "res://")
            include_addons: Whether to also scan res://addons (default False)
        """
        return await bridge.call_godot("find_script_references", {
            "query": query,
            "path": path,
            "include_addons": include_addons,
        })

    @mcp.tool()
    async def batch_add_nodes(
        nodes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Batch-add multiple nodes in a single operation.

        Args:
            nodes: Array of node definitions, each with:
                - type (str, required): Node class name (e.g. "Sprite2D")
                - parent_path (str, optional): Parent path (default ".")
                - name (str, optional): Node name
                - properties (dict, optional): Properties to set
        """
        return await bridge.call_godot("batch_add_nodes", {
            "nodes": nodes,
        })

    @mcp.tool()
    async def detect_circular_dependencies(
        path: str = "res://",
        include_addons: bool = False,
    ) -> dict[str, Any]:
        """Find circular scene dependencies in the project.

        Args:
            path: Directory to analyze (default "res://")
            include_addons: Whether to also scan res://addons (default False)
        """
        return await bridge.call_godot("detect_circular_dependencies", {
            "path": path,
            "include_addons": include_addons,
        })

    @mcp.tool()
    async def batch_execute(
        operations: list[dict[str, Any]],
        continue_on_error: bool = True,
    ) -> dict[str, Any]:
        """Execute a list of commands sequentially in a single tool call.

        This reduces AI agent round-trips when multiple operations need to be
        performed in sequence and intermediate results are not needed for decisions.

        Args:
            operations: List of operations, each with:
                - method (str, required): Command name (e.g. "add_node", "update_property")
                - params (dict, optional): Parameters for the command
            continue_on_error: Whether to continue executing after a failure (default True)
        """
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0

        for i, op in enumerate(operations):
            method = op.get("method", "")
            params = op.get("params", {})

            if not method:
                entry: dict[str, Any] = {
                    "index": i,
                    "method": "",
                    "status": "error",
                    "error": "Missing 'method' field in operation",
                }
                results.append(entry)
                failed += 1
                if not continue_on_error:
                    break
                continue

            try:
                result = await bridge.call_godot(method, params)
                entry = {
                    "index": i,
                    "method": method,
                    "status": "ok",
                    "result": result,
                }
                results.append(entry)
                succeeded += 1
            except Exception as e:
                entry = {
                    "index": i,
                    "method": method,
                    "status": "error",
                    "error": str(e),
                }
                results.append(entry)
                failed += 1
                if not continue_on_error:
                    break

        return {
            "results": results,
            "total": len(operations),
            "executed": len(results),
            "succeeded": succeeded,
            "failed": failed,
        }
