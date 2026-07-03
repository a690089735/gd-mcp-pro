"""TileMap tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def tilemap_set_cell(
        node_path: str,
        x: int,
        y: int,
        source_id: int = 0,
        atlas_x: int = 0,
        atlas_y: int = 0,
        layer: int = 0,
    ) -> dict[str, Any]:
        """Set a single tile cell in a TileMapLayer.

        Args:
            node_path: Path to the TileMapLayer node
            x: Cell X coordinate
            y: Cell Y coordinate
            source_id: Tile source ID (default 0)
            atlas_x: Atlas X coordinate (default 0)
            atlas_y: Atlas Y coordinate (default 0)
            layer: Layer index for legacy TileMap nodes (default 0)
        """
        return await bridge.call_godot("tilemap_set_cell", {
            "node_path": node_path,
            "x": x,
            "y": y,
            "source_id": source_id,
            "atlas_x": atlas_x,
            "atlas_y": atlas_y,
            "layer": layer,
        })

    @mcp.tool()
    async def tilemap_fill_rect(
        node_path: str,
        x: int,
        y: int,
        width: int,
        height: int,
        source_id: int = 0,
        atlas_x: int = 0,
        atlas_y: int = 0,
        layer: int = 0,
    ) -> dict[str, Any]:
        """Fill a rectangular region with tiles in a TileMapLayer.

        Args:
            node_path: Path to the TileMapLayer node
            x: Start X coordinate
            y: Start Y coordinate
            width: Rectangle width in cells
            height: Rectangle height in cells
            source_id: Tile source ID (default 0)
            atlas_x: Atlas X coordinate (default 0)
            atlas_y: Atlas Y coordinate (default 0)
            layer: Layer index for legacy TileMap nodes (default 0)
        """
        return await bridge.call_godot("tilemap_fill_rect", {
            "node_path": node_path,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "source_id": source_id,
            "atlas_x": atlas_x,
            "atlas_y": atlas_y,
            "layer": layer,
        })

    @mcp.tool()
    async def tilemap_get_cell(
        node_path: str,
        x: int,
        y: int,
        layer: int = 0,
    ) -> dict[str, Any]:
        """Get tile data at a specific cell.

        Args:
            node_path: Path to the TileMapLayer node
            x: Cell X coordinate
            y: Cell Y coordinate
            layer: Layer index for legacy TileMap nodes (default 0)
        """
        return await bridge.call_godot("tilemap_get_cell", {
            "node_path": node_path,
            "x": x,
            "y": y,
            "layer": layer,
        })

    @mcp.tool()
    async def tilemap_clear(
        node_path: str,
        layer: int = -1,
    ) -> dict[str, Any]:
        """Clear all cells in a TileMapLayer.

        Args:
            node_path: Path to the TileMapLayer node
            layer: Layer index for legacy TileMap nodes (-1 = clear all layers, default -1)
        """
        params: dict[str, Any] = {"node_path": node_path}
        if layer >= 0:
            params["layer"] = layer
        return await bridge.call_godot("tilemap_clear", params)

    @mcp.tool()
    async def tilemap_get_info(node_path: str) -> dict[str, Any]:
        """Get TileMapLayer info including tile set sources.

        Args:
            node_path: Path to the TileMapLayer node
        """
        return await bridge.call_godot("tilemap_get_info", {"node_path": node_path})

    @mcp.tool()
    async def tilemap_get_used_cells(
        node_path: str,
        layer: int = 0,
    ) -> dict[str, Any]:
        """Get list of all used cells in a TileMapLayer.

        Args:
            node_path: Path to the TileMapLayer node
            layer: Layer index for legacy TileMap nodes (default 0)
        """
        return await bridge.call_godot("tilemap_get_used_cells", {
            "node_path": node_path,
            "layer": layer,
        })