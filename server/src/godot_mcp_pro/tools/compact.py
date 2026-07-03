"""Compact mode: all 175 tools merged into ~21 domain tools + batch_execute.

Activated via --compact CLI argument. Each tool dispatches to GDScript commands
based on the 'action' parameter.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..bridge import GodotBridge


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any]:
    """Remove None values from params dict."""
    if not params:
        return {}
    return {k: v for k, v in params.items() if v is not None}


def _dispatch(action: str, action_map: dict[str, str], tool_name: str) -> str:
    """Resolve action to GDScript method name."""
    method = action_map.get(action)
    if not method:
        raise ValueError(
            f"Unknown action '{action}' for {tool_name}. "
            f"Available: {sorted(action_map.keys())}"
        )
    return method


def register(mcp: FastMCP, bridge: GodotBridge):
    """Register all compact mode tools."""

    # =========================================================================
    # 1. PROJECT — project info, filesystem, search, settings
    # =========================================================================
    @mcp.tool()
    async def project(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Project & filesystem operations.

        Actions:
        - info: Get project metadata (no params)
        - tree: Get filesystem tree (path:str="res://", filter:str="", max_depth:int=10)
        - search: Fuzzy/glob file search (query:str, path:str="res://", file_type:str="", max_results:int=50)
        - search_content: Search inside files (query:str, path:str="res://", max_results:int=50, regex:bool=false, file_type:str="")
        - get_settings: Read project settings (section:str="", key:str="")
        - set_setting: Set a project setting (key:str, value:any)
        - uid_to_path: Convert UID to path (uid:str)
        - path_to_uid: Convert path to UID (path:str)
        """
        ACTION_MAP = {
            "info": "get_project_info",
            "tree": "get_filesystem_tree",
            "search": "search_files",
            "search_content": "search_in_files",
            "get_settings": "get_project_settings",
            "set_setting": "set_project_setting",
            "uid_to_path": "uid_to_project_path",
            "path_to_uid": "project_path_to_uid",
        }
        method = _dispatch(action, ACTION_MAP, "project")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 2. SCENE — scene tree, create/open/delete/save, play/stop
    # =========================================================================
    @mcp.tool()
    async def scene(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Scene management operations.

        Actions:
        - tree: Get live scene tree (max_depth:int=-1)
        - file_content: Get raw .tscn content (path:str)
        - create: Create new scene (path:str, root_type:str="Node2D", root_name:str="")
        - open: Open scene in editor (path:str)
        - delete: Delete scene file (path:str)
        - instance: Instance scene as child (scene_path:str, parent_path:str=".", name:str="")
        - play: Run scene (mode:str="main", scene_path:str="")
        - stop: Stop running scene (no params)
        - save: Save current scene (path:str="")
        - exports: Get scene's exported vars (path:str)
        """
        ACTION_MAP = {
            "tree": "get_scene_tree",
            "file_content": "get_scene_file_content",
            "create": "create_scene",
            "open": "open_scene",
            "delete": "delete_scene",
            "instance": "add_scene_instance",
            "play": "play_scene",
            "stop": "stop_scene",
            "save": "save_scene",
            "exports": "get_scene_exports",
        }
        method = _dispatch(action, ACTION_MAP, "scene")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 3. NODE — add/delete/duplicate/move/rename, properties, signals, groups
    # =========================================================================
    @mcp.tool()
    async def node(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Node manipulation operations.

        Actions:
        - add: Add node (type:str, parent_path:str=".", name:str="", properties:dict={})
        - delete: Delete node (node_path:str)
        - duplicate: Duplicate node (node_path:str, name:str="")
        - move: Move/reparent (node_path:str, new_parent_path:str)
        - rename: Rename node (node_path:str, new_name:str)
        - update_property: Set property (node_path:str, property:str, value:any)
        - get_properties: Get all properties (node_path:str, category:str="")
        - add_resource: Add resource to property (node_path:str, property:str, resource_type:str, resource_properties:dict={})
        - set_anchor: Set anchor preset (node_path:str, preset:str, keep_offsets:bool=false)
        - connect_signal: Connect signal (source_path:str, signal_name:str, target_path:str, method_name:str)
        - disconnect_signal: Disconnect signal (source_path:str, signal_name:str, target_path:str, method_name:str)
        - get_groups: Get groups (node_path:str)
        - set_groups: Set groups (node_path:str, groups:list)
        - find_in_group: Find nodes in group (group:str)
        - get_selection: Get editor selection (top_only:bool=false)
        - select: Select nodes (node_path:str="", node_paths:list=null, mode:str="replace", inspect:bool=true, focus:bool=true, inspector_only:bool=false, for_property:str="")
        - clear_selection: Clear selection (no params)
        """
        ACTION_MAP = {
            "add": "add_node",
            "delete": "delete_node",
            "duplicate": "duplicate_node",
            "move": "move_node",
            "rename": "rename_node",
            "update_property": "update_property",
            "get_properties": "get_node_properties",
            "add_resource": "add_resource",
            "set_anchor": "set_anchor_preset",
            "connect_signal": "connect_signal",
            "disconnect_signal": "disconnect_signal",
            "get_groups": "get_node_groups",
            "set_groups": "set_node_groups",
            "find_in_group": "find_nodes_in_group",
            "get_selection": "get_editor_selection",
            "select": "select_nodes",
            "clear_selection": "clear_editor_selection",
        }
        method = _dispatch(action, ACTION_MAP, "node")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 4. SCRIPT — list/read/create/edit/attach/validate
    # =========================================================================
    @mcp.tool()
    async def script(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Script management operations.

        Actions:
        - list: List scripts (path:str="res://", recursive:bool=true)
        - read: Read script content (path:str)
        - create: Create script (path:str, content:str="", extends:str="", class_name:str="", force:bool=false)
        - edit: Edit script (path:str, content:str="", search:str="", replace:str="", regex:bool=false, line:int=-1, insert:str="", start_line:int=-1, end_line:int=-1, force:bool=false)
        - attach: Attach script to node (node_path:str, script_path:str)
        - open_scripts: Get open scripts in editor (no params)
        - validate: Validate GDScript syntax (path:str)
        """
        ACTION_MAP = {
            "list": "list_scripts",
            "read": "read_script",
            "create": "create_script",
            "edit": "edit_script",
            "attach": "attach_script",
            "open_scripts": "get_open_scripts",
            "validate": "validate_script",
        }
        method = _dispatch(action, ACTION_MAP, "script")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 5. EDITOR — errors, output, screenshots, execute, reload, camera
    # =========================================================================
    @mcp.tool()
    async def editor(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Editor control operations.

        Actions:
        - errors: Get editor errors (no params)
        - output_log: Get output panel (lines:int=100)
        - editor_screenshot: Screenshot editor viewport (save_path:str="")
        - game_screenshot: Screenshot running game (save_path:str="")
        - execute_script: Run GDScript in editor (code:str, allow_unsafe_editor_io:bool=false)
        - clear_output: Clear output panel (no params)
        - get_signals: Get node signals (node_path:str)
        - reload_plugin: Reload MCP plugin (no params)
        - reload_project: Rescan filesystem (no params)
        - auto_dismiss: Set auto-dismiss dialogs (enabled:bool=true)
        - get_camera: Get 3D editor camera (no params)
        - set_camera: Set 3D editor camera (position:dict=null, rotation:dict=null, distance:float=null)
        """
        ACTION_MAP = {
            "errors": "get_editor_errors",
            "output_log": "get_output_log",
            "editor_screenshot": "get_editor_screenshot",
            "game_screenshot": "get_game_screenshot",
            "execute_script": "execute_editor_script",
            "clear_output": "clear_output",
            "get_signals": "get_signals",
            "reload_plugin": "reload_plugin",
            "reload_project": "reload_project",
            "auto_dismiss": "set_auto_dismiss",
            "get_camera": "get_editor_camera",
            "set_camera": "set_editor_camera",
        }
        method = _dispatch(action, ACTION_MAP, "editor")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 6. INPUT — simulate key/mouse/action, sequences, action config
    # =========================================================================
    @mcp.tool()
    async def input(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Input simulation operations (for running game).

        Actions:
        - key: Simulate key press (keycode:str, pressed:bool=true, shift:bool=false, ctrl:bool=false, alt:bool=false)
        - mouse_click: Simulate mouse click (x:float=0, y:float=0, button:int=1, pressed:bool=true, double_click:bool=false)
        - mouse_move: Simulate mouse move (x:float=0, y:float=0, relative_x:float=0, relative_y:float=0)
        - simulate: Simulate input action (action:str, pressed:bool=true, strength:float=1.0)
        - sequence: Execute input sequence (events:list)
        - get_actions: List all input actions (no params)
        - define: Create/modify input action (action:str, events:list=null, deadzone:float=0.5)
        """
        ACTION_MAP = {
            "key": "simulate_key",
            "mouse_click": "simulate_mouse_click",
            "mouse_move": "simulate_mouse_move",
            "simulate": "simulate_action",
            "sequence": "simulate_sequence",
            "get_actions": "get_input_actions",
            "define": "set_input_action",
        }
        method = _dispatch(action, ACTION_MAP, "input")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 7. RUNTIME — game inspection, node props, recording, UI, navigation
    # =========================================================================
    @mcp.tool()
    async def runtime(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Runtime game inspection & control.

        Actions:
        - game_tree: Get game scene tree (max_depth:int=-1)
        - get_properties: Get game node properties (node_path:str)
        - set_property: Set game node property (node_path:str, property:str, value:any)
        - execute_script: Run GDScript in game (code:str)
        - capture_frames: Capture screenshots (count:int=1, interval:float=0.5, save_path:str="")
        - monitor: Monitor properties over time (node_path:str, properties:list, duration:float=1.0, interval:float=0.1)
        - start_recording: Start input recording (name:str="")
        - stop_recording: Stop recording (no params)
        - replay: Replay recording (name:str="")
        - find_by_script: Find nodes by script (script_path:str)
        - get_autoload: Get autoload singleton (name:str)
        - batch_get: Batch get properties (requests:list)
        - find_ui: Find UI elements (root_path:str="", type_filter:str="")
        - click_button: Click button by text (text:str)
        - wait_for_node: Wait for node (node_path:str, timeout:float=5.0)
        - find_nearby: Find nearby nodes (position_x:float, position_y:float, radius:float=100.0, type_filter:str="")
        - navigate_to: Navigate via pathfinding (node_path:str, target_x:float, target_y:float)
        - move_to: Walk to position (node_path:str, target_x:float, target_y:float, speed:float=100.0)
        - watch_signals: Watch signal emissions (node_paths:list, signal_filter:list=null, duration_ms:int=5000)
        """
        ACTION_MAP = {
            "game_tree": "get_game_scene_tree",
            "get_properties": "get_game_node_properties",
            "set_property": "set_game_node_property",
            "execute_script": "execute_game_script",
            "capture_frames": "capture_frames",
            "monitor": "monitor_properties",
            "start_recording": "start_recording",
            "stop_recording": "stop_recording",
            "replay": "replay_recording",
            "find_by_script": "find_nodes_by_script",
            "get_autoload": "get_autoload",
            "batch_get": "batch_get_properties",
            "find_ui": "find_ui_elements",
            "click_button": "click_button_by_text",
            "wait_for_node": "wait_for_node",
            "find_nearby": "find_nearby_nodes",
            "navigate_to": "navigate_to",
            "move_to": "move_to",
            "watch_signals": "watch_signals",
        }
        method = _dispatch(action, ACTION_MAP, "runtime")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 8. ANIMATION — animations, tracks, keyframes, tree, state machine
    # =========================================================================
    @mcp.tool()
    async def animation(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Animation & AnimationTree operations.

        Actions:
        - list: List animations (node_path:str)
        - create: Create animation (node_path:str, name:str, length:float=1.0, loop:bool=false)
        - add_track: Add track (node_path:str, animation:str, track_type:str, track_path:str)
        - set_keyframe: Insert keyframe (node_path:str, animation:str, track_index:int, time:float, value:any)
        - info: Get animation info (node_path:str, animation:str)
        - remove: Remove animation (node_path:str, animation:str)
        - create_tree: Create AnimationTree (node_path:str, root_type:str="state_machine")
        - tree_structure: Get tree structure (node_path:str)
        - set_param: Set tree parameter (node_path:str, parameter:str, value:any)
        - add_state: Add state machine state (node_path:str, state_name:str, animation:str="", state_machine_path:str="")
        - remove_state: Remove state (node_path:str, state_name:str, state_machine_path:str="")
        - add_transition: Add transition (node_path:str, from_state:str, to_state:str, advance_condition:str="", auto_advance:bool=false, state_machine_path:str="")
        - remove_transition: Remove transition (node_path:str, from_state:str, to_state:str, state_machine_path:str="")
        - set_blend_node: Configure blend tree node (node_path:str, blend_node_name:str, blend_node_type:str, properties:dict=null)
        """
        ACTION_MAP = {
            "list": "list_animations",
            "create": "create_animation",
            "add_track": "add_animation_track",
            "set_keyframe": "set_animation_keyframe",
            "info": "get_animation_info",
            "remove": "remove_animation",
            "create_tree": "create_animation_tree",
            "tree_structure": "get_animation_tree_structure",
            "set_param": "set_tree_parameter",
            "add_state": "add_state_machine_state",
            "remove_state": "remove_state_machine_state",
            "add_transition": "add_state_machine_transition",
            "remove_transition": "remove_state_machine_transition",
            "set_blend_node": "set_blend_tree_node",
        }
        method = _dispatch(action, ACTION_MAP, "animation")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 9. TILEMAP — set/get/fill/clear cells, info
    # =========================================================================
    @mcp.tool()
    async def tilemap(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """TileMap operations.

        Actions:
        - set_cell: Set a tile (node_path:str, x:int, y:int, source_id:int=0, atlas_x:int=0, atlas_y:int=0, layer:int=0)
        - fill_rect: Fill rectangle (node_path:str, x:int, y:int, width:int, height:int, source_id:int=0, atlas_x:int=0, atlas_y:int=0, layer:int=0)
        - get_cell: Get tile data (node_path:str, x:int, y:int, layer:int=0)
        - clear: Clear all cells (node_path:str, layer:int=-1)
        - info: Get tilemap info (node_path:str)
        - used_cells: Get used cells list (node_path:str, layer:int=0)
        """
        ACTION_MAP = {
            "set_cell": "tilemap_set_cell",
            "fill_rect": "tilemap_fill_rect",
            "get_cell": "tilemap_get_cell",
            "clear": "tilemap_clear",
            "info": "tilemap_get_info",
            "used_cells": "tilemap_get_used_cells",
        }
        method = _dispatch(action, ACTION_MAP, "tilemap")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 10. UI — theme, control setup
    # =========================================================================
    @mcp.tool()
    async def ui(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """UI/Theme/Control operations.

        Actions:
        - create_theme: Create theme resource (path:str, base_type:str="")
        - set_color: Set theme color (node_path:str, name:str, color:str, theme_type:str="")
        - set_constant: Set theme constant (node_path:str, name:str, value:int, theme_type:str="")
        - set_font_size: Set font size (node_path:str, name:str, size:int, theme_type:str="")
        - set_stylebox: Set StyleBoxFlat (node_path:str, name:str, properties:dict=null, theme_type:str="")
        - theme_info: Get theme overrides (node_path:str)
        - setup_control: Configure control layout (node_path:str, anchor_preset:str="", min_size_x:float=null, min_size_y:float=null, size_flags_h:str="", size_flags_v:str="", theme_path:str="")
        """
        ACTION_MAP = {
            "create_theme": "create_theme",
            "set_color": "set_theme_color",
            "set_constant": "set_theme_constant",
            "set_font_size": "set_theme_font_size",
            "set_stylebox": "set_theme_stylebox",
            "theme_info": "get_theme_info",
            "setup_control": "setup_control",
        }
        method = _dispatch(action, ACTION_MAP, "ui")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 11. PHYSICS — physics body, collision, layers, raycast
    # =========================================================================
    @mcp.tool()
    async def physics(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Physics & collision operations.

        Actions:
        - setup_body: Configure physics body (node_path:str, properties:dict=null)
        - setup_collision: Add collision shape (node_path:str, shape_type:str, shape_properties:dict=null)
        - set_layers: Set collision layer/mask (node_path:str, layer:int=null, mask:int=null)
        - get_layers: Get layer/mask info (node_path:str)
        - collision_info: Get collision shapes (node_path:str)
        - add_raycast: Add RayCast node (node_path:str, target_x:float=0, target_y:float=-50, target_z:float=0, is_3d:bool=false)
        """
        ACTION_MAP = {
            "setup_body": "setup_physics_body",
            "setup_collision": "setup_collision",
            "set_layers": "set_physics_layers",
            "get_layers": "get_physics_layers",
            "collision_info": "get_collision_info",
            "add_raycast": "add_raycast",
        }
        method = _dispatch(action, ACTION_MAP, "physics")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 12. SCENE_3D — mesh, camera, lighting, environment, gridmap, materials
    # =========================================================================
    @mcp.tool()
    async def scene_3d(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """3D scene operations.

        Actions:
        - add_mesh: Add MeshInstance3D (parent_path:str=".", mesh_type:str="box", name:str="", properties:dict=null)
        - setup_camera: Configure Camera3D (node_path:str="", properties:dict=null)
        - setup_lighting: Add/configure light (light_type:str="directional", parent_path:str=".", name:str="", properties:dict=null)
        - setup_environment: Configure WorldEnvironment (node_path:str="", properties:dict=null)
        - add_gridmap: Add GridMap (parent_path:str=".", name:str="", mesh_library_path:str="")
        - set_material: Set StandardMaterial3D (node_path:str, properties:dict=null)
        """
        ACTION_MAP = {
            "add_mesh": "add_mesh_instance",
            "setup_camera": "setup_camera_3d",
            "setup_lighting": "setup_lighting",
            "setup_environment": "setup_environment",
            "add_gridmap": "add_gridmap",
            "set_material": "set_material_3d",
        }
        method = _dispatch(action, ACTION_MAP, "scene_3d")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 13. PARTICLES — create, material, gradient, presets, info
    # =========================================================================
    @mcp.tool()
    async def particles(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Particle system operations.

        Actions:
        - create: Create particles node (parent_path:str=".", is_3d:bool=false, name:str="", properties:dict=null)
        - set_material: Set particle material (node_path:str, properties:dict=null)
        - set_gradient: Set color gradient (node_path:str, colors:list, offsets:list=null)
        - apply_preset: Apply preset (node_path:str, preset:str) [fire/smoke/sparks/snow/rain/explosion/magic/dust]
        - info: Get particle info (node_path:str)
        """
        ACTION_MAP = {
            "create": "create_particles",
            "set_material": "set_particle_material",
            "set_gradient": "set_particle_color_gradient",
            "apply_preset": "apply_particle_preset",
            "info": "get_particle_info",
        }
        method = _dispatch(action, ACTION_MAP, "particles")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 14. NAVIGATION — region, agent, bake, layers, info
    # =========================================================================
    @mcp.tool()
    async def navigation(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Navigation operations.

        Actions:
        - setup_region: Configure NavigationRegion (node_path:str="", parent_path:str=".", is_3d:bool=false, properties:dict=null)
        - setup_agent: Configure NavigationAgent (node_path:str="", parent_path:str=".", is_3d:bool=false, properties:dict=null)
        - bake: Bake navigation mesh (node_path:str)
        - set_layers: Set navigation layers (node_path:str, layers:int)
        - info: Get navigation info (node_path:str="")
        """
        ACTION_MAP = {
            "setup_region": "setup_navigation_region",
            "setup_agent": "setup_navigation_agent",
            "bake": "bake_navigation_mesh",
            "set_layers": "set_navigation_layers",
            "info": "get_navigation_info",
        }
        method = _dispatch(action, ACTION_MAP, "navigation")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 15. AUDIO — player, bus, effects, layout
    # =========================================================================
    @mcp.tool()
    async def audio(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Audio operations.

        Actions:
        - add_player: Add AudioStreamPlayer (parent_path:str=".", name:str="", stream_path:str="", is_3d:bool=false, properties:dict=null)
        - add_bus: Add audio bus (name:str, send:str="Master")
        - add_effect: Add bus effect (bus:str, effect_type:str, properties:dict=null)
        - set_bus: Configure bus (bus:str, properties:dict=null)
        - bus_layout: Get bus layout (no params)
        - info: Get audio info (node_path:str="")
        """
        ACTION_MAP = {
            "add_player": "add_audio_player",
            "add_bus": "add_audio_bus",
            "add_effect": "add_audio_bus_effect",
            "set_bus": "set_audio_bus",
            "bus_layout": "get_audio_bus_layout",
            "info": "get_audio_info",
        }
        method = _dispatch(action, ACTION_MAP, "audio")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 16. SHADER — create/read/edit, assign, params
    # =========================================================================
    @mcp.tool()
    async def shader(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Shader operations.

        Actions:
        - create: Create shader file (path:str, content:str="", shader_type:str="spatial", force:bool=false)
        - read: Read shader content (path:str)
        - edit: Edit shader (path:str, content:str="", search:str="", replace:str="", force:bool=false)
        - assign: Assign ShaderMaterial to node (node_path:str, shader_path:str)
        - set_param: Set shader parameter (node_path:str, param:str, value:any)
        - get_params: Get shader parameters (node_path:str)
        """
        ACTION_MAP = {
            "create": "create_shader",
            "read": "read_shader",
            "edit": "edit_shader",
            "assign": "assign_shader_material",
            "set_param": "set_shader_param",
            "get_params": "get_shader_params",
        }
        method = _dispatch(action, ACTION_MAP, "shader")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 17. RESOURCE — read/edit/create resource, preview, autoload
    # =========================================================================
    @mcp.tool()
    async def resource(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Resource management operations.

        Actions:
        - read: Read .tres resource (path:str)
        - edit: Edit resource properties (path:str, properties:dict)
        - create: Create .tres resource (path:str, type:str, properties:dict=null)
        - preview: Get resource thumbnail (path:str)
        - add_autoload: Register autoload (name:str, path:str)
        - remove_autoload: Remove autoload (name:str)
        """
        ACTION_MAP = {
            "read": "read_resource",
            "edit": "edit_resource",
            "create": "create_resource",
            "preview": "get_resource_preview",
            "add_autoload": "add_autoload",
            "remove_autoload": "remove_autoload",
        }
        method = _dispatch(action, ACTION_MAP, "resource")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 18. BATCH — find, batch operations, references, dependencies
    # =========================================================================
    @mcp.tool()
    async def batch(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Batch & search operations.

        Actions:
        - find_by_type: Find nodes by type (type:str, recursive:bool=true)
        - find_signals: Find signal connections (node_path:str="")
        - set_property: Batch set property by type (type:str, property:str, value:any, node_path:str="")
        - find_references: Search files for pattern (pattern:str, path:str="res://")
        - dependencies: Get scene dependencies (path:str="")
        - cross_scene_set: Set property across scenes (type:str, property:str, value:any, scene_paths:list=[], force:bool=false, dry_run:bool=null)
        - script_references: Find script usage (path:str)
        - add_nodes: Batch add nodes (nodes:list)
        - circular_deps: Detect circular dependencies (path:str="res://")
        """
        ACTION_MAP = {
            "find_by_type": "find_nodes_by_type",
            "find_signals": "find_signal_connections",
            "set_property": "batch_set_property",
            "find_references": "find_node_references",
            "dependencies": "get_scene_dependencies",
            "cross_scene_set": "cross_scene_set_property",
            "script_references": "find_script_references",
            "add_nodes": "batch_add_nodes",
            "circular_deps": "detect_circular_dependencies",
        }
        method = _dispatch(action, ACTION_MAP, "batch")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 19. TEST — scenarios, assertions, stress test
    # =========================================================================
    @mcp.tool()
    async def test(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Testing & assertion operations.

        Actions:
        - run_scenario: Run test scenario (steps:list, name:str="", scene_path:str="")
        - assert_state: Assert node property (node_path:str, property:str, expected:any, operator:str="eq")
        - assert_text: Assert screen text (text:str, partial:bool=true, case_sensitive:bool=true)
        - compare_screenshots: Compare images (image_a:str, image_b:str, threshold:float=0.95)
        - stress_test: Run stress test (duration:float=5.0, actions:list=null)
        - report: Get test report (no params)
        """
        ACTION_MAP = {
            "run_scenario": "run_test_scenario",
            "assert_state": "assert_node_state",
            "assert_text": "assert_screen_text",
            "compare_screenshots": "compare_screenshots",
            "stress_test": "run_stress_test",
            "report": "get_test_report",
        }
        method = _dispatch(action, ACTION_MAP, "test")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 20. EXPORT — presets, export, android
    # =========================================================================
    @mcp.tool()
    async def export(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Export & deployment operations.

        Actions:
        - list_presets: List export presets (no params)
        - export: Export project (preset:str)
        - info: Get export info (no params)
        - list_android: List Android devices (no params)
        - android_info: Get Android preset info (preset:str="")
        - deploy_android: Deploy to Android (device_serial:str="", preset:str="")
        """
        ACTION_MAP = {
            "list_presets": "list_export_presets",
            "export": "export_project",
            "info": "get_export_info",
            "list_android": "list_android_devices",
            "android_info": "get_android_preset_info",
            "deploy_android": "deploy_to_android",
        }
        method = _dispatch(action, ACTION_MAP, "export")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 21. DIAGNOSTICS — analysis, profiling, statistics
    # =========================================================================
    @mcp.tool()
    async def diagnostics(action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Diagnostics, analysis & profiling operations.

        Actions:
        - scene_complexity: Analyze scene metrics (path:str="")
        - signal_flow: Map signal connections (node_path:str="")
        - unused_resources: Find unused resources (path:str="res://")
        - statistics: Get project statistics (no params)
        - performance: Get performance monitors (no params)
        - editor_performance: Get editor performance (no params)
        """
        ACTION_MAP = {
            "scene_complexity": "analyze_scene_complexity",
            "signal_flow": "analyze_signal_flow",
            "unused_resources": "find_unused_resources",
            "statistics": "get_project_statistics",
            "performance": "get_performance_monitors",
            "editor_performance": "get_editor_performance",
        }
        method = _dispatch(action, ACTION_MAP, "diagnostics")
        return await bridge.call_godot(method, _clean_params(params))

    # =========================================================================
    # 22. BATCH_EXECUTE — execute multiple commands sequentially
    # =========================================================================
    @mcp.tool()
    async def batch_execute(
        operations: list[dict[str, Any]],
        continue_on_error: bool = True,
    ) -> dict[str, Any]:
        """Execute a list of GDScript commands sequentially in a single tool call.

        Reduces AI agent round-trips when multiple operations need to be
        performed in sequence.

        Args:
            operations: List of operations, each with:
                - method (str, required): GDScript command name (e.g. "add_node", "update_property")
                - params (dict, optional): Parameters for the command
            continue_on_error: Whether to continue after a failure (default True)
        """
        results: list[dict[str, Any]] = []
        succeeded = 0
        failed = 0

        for i, op in enumerate(operations):
            method = op.get("method", "")
            op_params = op.get("params", {})

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
                result = await bridge.call_godot(method, op_params)
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