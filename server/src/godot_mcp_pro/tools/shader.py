"""Shader tools."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def register(mcp: FastMCP, bridge: GodotBridge):
    @mcp.tool()
    async def create_shader(
        path: str,
        content: str = "",
        shader_type: str = "spatial",
    ) -> dict[str, Any]:
        """Create a shader file with optional template.

        Args:
            path: Where to save the shader (e.g. "res://shaders/dissolve.gdshader")
            content: Shader content (if empty, generates template)
            shader_type: Shader type: "spatial", "canvas_item", or "particles" (default "spatial")
        """
        return await bridge.call_godot("create_shader", {
            "path": path,
            "content": content,
            "shader_type": shader_type,
        })

    @mcp.tool()
    async def read_shader(path: str) -> dict[str, Any]:
        """Read a shader file content.

        Args:
            path: Path to the shader file
        """
        return await bridge.call_godot("read_shader", {"path": path})

    @mcp.tool()
    async def edit_shader(
        path: str,
        content: str = "",
        search: str = "",
        replace: str = "",
    ) -> dict[str, Any]:
        """Edit a shader file (full replace or search-and-replace).

        Args:
            path: Path to the shader file
            content: Full replacement content (replaces entire file)
            search: Text to search for (used with replace)
            replace: Replacement text
        """
        return await bridge.call_godot("edit_shader", {
            "path": path,
            "content": content,
            "search": search,
            "replace": replace,
        })

    @mcp.tool()
    async def assign_shader_material(
        node_path: str,
        shader_path: str,
    ) -> dict[str, Any]:
        """Assign a ShaderMaterial to a node.

        Args:
            node_path: Path to the node
            shader_path: Path to the shader file
        """
        return await bridge.call_godot("assign_shader_material", {
            "node_path": node_path,
            "shader_path": shader_path,
        })

    @mcp.tool()
    async def set_shader_param(
        node_path: str,
        param: str,
        value: Any,
    ) -> dict[str, Any]:
        """Set a shader parameter on a node's ShaderMaterial.

        Args:
            node_path: Path to the node with ShaderMaterial
            param: Parameter name
            value: Parameter value (supports smart type parsing)
        """
        return await bridge.call_godot("set_shader_param", {
            "node_path": node_path,
            "param": param,
            "value": value,
        })

    @mcp.tool()
    async def get_shader_params(node_path: str) -> dict[str, Any]:
        """Get all shader parameters from a node's ShaderMaterial.

        Args:
            node_path: Path to the node with ShaderMaterial
        """
        return await bridge.call_godot("get_shader_params", {"node_path": node_path})