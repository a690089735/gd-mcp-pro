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
        - tree: Get filesystem tree (path:str="res://", filter:str="" [filename glob, e.g. "*.gd"], max_depth:int=10)
        - search: Fuzzy/glob file search (query:str, path:str="res://", file_type:str="" [bare extension, e.g. "gd"], max_results:int=50)
        - search_content: Search inside files (query:str, path:str="res://", max_results:int=50, regex:bool=false, file_type:str="" [bare extension, e.g. "gd"])
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
        - tree: Get live scene tree, scene-relative paths with root="." (max_depth:int=-1)
        - file_content: Get raw .tscn content (path:str)
        - create: Create new scene (path:str, root_type:str="Node2D", root_name:str="")
        - open: Open scene in editor (path:str)
        - delete: Delete scene file (path:str)
        - instance: Instance scene as child (scene_path:str, parent_path:str=".", name:str="")
        - play: Run scene (mode:str="main"|"current"|"res://path.tscn" — pass a
          scene path directly as `mode` to run a custom scene)
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
        - get_properties: Get all properties (node_path:str, category:str="" [property-name prefix, e.g. "texture"])
        - add_resource: Add resource to property (node_path:str, property:str, resource_type:str, resource_properties:dict={})
        - set_anchor: Set anchor preset (node_path:str, preset:str, keep_offsets:bool=false)
        - connect_signal: Connect signal, persistent/saved into .tscn (source_path:str, signal_name:str, target_path:str, method_name:str, deferred:bool=false, one_shot:bool=false)
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
        - create: Create script (path:str, content:str="", extends:str="Node", class_name:str="", force:bool=false)
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
        - errors: Get editor errors (max_lines:int=100)
        - output_log: Get output panel (max_lines:int=100, filter:str="")
        - editor_screenshot: Screenshot editor viewport (save_path:str="")
        - game_screenshot: Screenshot running game (save_path:str="")
        - execute_script: Run GDScript in editor (code:str, allow_unsafe_editor_io:bool=false).
          Use `_mcp_print(v)` for captured `output`; plain `print()` is NOT captured.
          `return v` is reported as `return_value`.
        - clear_output: Clear output panel (no params)
        - get_signals: Get node signals (node_path:str)
        - reload_plugin: Reload MCP plugin (no params)
        - reload_project: Rescan filesystem (no params)
        - auto_dismiss: Set auto-dismiss dialogs (enabled:bool=true)
        - get_camera: Get 3D editor camera (no params)
        - set_camera: Set 3D editor camera (position:dict{x,y,z}, rotation_degrees:dict{x,y,z},
          look_at:dict{x,y,z} [overrides rotation], fov:float)
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
        - mouse_click: Simulate mouse click (x:float=0, y:float=0, button:int=1, pressed:bool=true, double_click:bool=false, auto_release:bool=true)
        - mouse_move: Simulate mouse move (x:float=0, y:float=0, relative_x:float=0, relative_y:float=0, button_mask:int=0, unhandled:bool=false)
        - simulate: Simulate input action (action:str, pressed:bool=true, strength:float=1.0)
        - sequence: Execute input sequence (events:list, frame_delay:int=0)
        - get_actions: List all input actions (filter:str="", include_builtin:bool=false)
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
        - game_tree: Get game scene tree (max_depth:int=-1, type_filter:str="", script_filter:str="", named_only:bool=false)
        - get_properties: Get game node properties (node_path:str, properties:list=null)
        - set_property: Set game node property (node_path:str, property:str, value:any)
        - execute_script: Run GDScript in game (code:str)
        - capture_frames: Capture screenshots (count:int=5, frame_interval:int=10, half_resolution:bool=true) [frames, not seconds]
        - monitor: Monitor properties over time (node_path:str, properties:list, frame_count:int=60, frame_interval:int=1) [frames, not seconds]
        - start_recording: Start input recording (no params)
        - stop_recording: Stop recording, returns captured events (no params)
        - replay: Replay recording (events:list from stop_recording, speed:float=1.0)
        - find_by_script: Find nodes by script (script:str, properties:list=null)
        - get_autoload: Get autoload singleton (name:str, properties:list=null)
        - batch_get: Batch get properties (nodes:list of {node_path, properties})
        - find_ui: Find UI elements (type_filter:str="")
        - click_button: Click button by text (text:str, partial:bool=false)
        - wait_for_node: Wait for node (node_path:str, timeout:float=5.0, poll_frames:int=5)
        - find_nearby: Find nearby nodes (position:str|dict{x,y,z}, radius:float=100.0, type_filter:str="", group_filter:str="", max_results:int=0)
        - navigate_to: Navigate via pathfinding (target:str|dict{x,y,z}, player_path:str="", camera_path:str="", move_speed:float=0)
        - move_to: Walk to position (target:str|dict{x,y,z}, player_path:str="", camera_path:str="", arrival_radius:float=0, timeout:float=15.0, run:bool=false, look_at_target:bool=false)
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
        - create: Create animation (node_path:str, name:str, length:float=1.0, loop_mode:int=0) [0=none,1=linear,2=pingpong]
        - add_track: Add track (node_path:str, animation:str, track_path:str,
          track_type:str="value"|"position_2d"|"rotation_2d"|"scale_2d"|"method"|"bezier"|"blend_shape"
          [unknown values fall back to "value"], update_mode:str="" ["value" tracks only])
        - set_keyframe: Insert keyframe (node_path:str, animation:str, track_index:int, time:float, value:any, easing:float=1.0)
        - info: Get animation info (node_path:str, animation:str)
        - remove: Remove animation (node_path:str, name:str)
        - create_tree: Create AnimationTree, root is a StateMachine (node_path:str, anim_player:str="", name:str="AnimationTree")
        - tree_structure: Get tree structure (node_path:str)
        - set_param: Set tree parameter (node_path:str, parameter:str, value:any)
        - add_state: Add state machine state (node_path:str, state_name:str, animation:str="", state_machine_path:str="", state_type:str="animation", position_x:float=0, position_y:float=0)
        - remove_state: Remove state (node_path:str, state_name:str, state_machine_path:str="")
        - add_transition: Add transition (node_path:str, from_state:str, to_state:str, advance_expression:str="", advance_mode:str="enabled"|"auto", switch_mode:str="immediate"|"sync"|"at_end", xfade_time:float=0, state_machine_path:str="")
        - remove_transition: Remove transition (node_path:str, from_state:str, to_state:str, state_machine_path:str="")
        - set_blend_node: Create blend tree node (node_path:str, blend_tree_state:str, bt_node_name:str, bt_node_type:str [CamelCase: Animation/Add2/Add3/Sub2/Blend2/Blend3/TimeScale/TimeSeek/Transition/OneShot], animation:str="", position_x:float=0, position_y:float=0, state_machine_path:str="", connect_to:str="", connect_port:int=0)
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
        - set_cell: Set a tile (node_path:str, x:int, y:int, source_id:int=0, atlas_x:int=0, atlas_y:int=0, layer:int=0, alternative:int=0)
        - fill_rect: Fill inclusive rect (node_path:str, x1:int, y1:int, x2:int, y2:int, source_id:int=0, atlas_x:int=0, atlas_y:int=0, layer:int=0, alternative:int=0)
        - get_cell: Get tile data (node_path:str, x:int, y:int, layer:int=0)
        - clear: Clear all cells (node_path:str, layer:int=-1)
        - info: Get tilemap info (node_path:str)
        - used_cells: Get used cells list (node_path:str, layer:int=0, max_count:int=0)
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
        - create_theme: Create theme resource, parent dirs auto-created (path:str, default_font_size:int=0)
        - set_color: Set theme color override (node_path:str, name:str, color:str, theme_type:str="")
        - set_constant: Set theme constant override (node_path:str, name:str, value:int)
        - set_font_size: Set font size override (node_path:str, name:str, size:int)
        - set_stylebox: Set StyleBoxFlat override (node_path:str, name:str, bg_color, border_color, border_width:int, corner_radius:int, padding:int)
        - theme_info: Get theme overrides (node_path:str)
        - setup_control: Configure control layout (node_path:str, anchor_preset:str="",
          min_size:str="Vector2(w, h)", size_flags_h:str="", size_flags_v:str="",
          grow_h:str="begin"|"end"|"both", grow_v:str, margins:dict{left,top,right,bottom}
          [MarginContainer only], separation:int [BoxContainer only])
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
        - setup_body: Configure physics body — flat keys: mass, gravity_scale, linear_damp,
          angular_damp, freeze, freeze_mode, contact_monitor, max_contacts_reported,
          continuous_cd, floor_max_angle, floor_snap_length, floor_stop_on_slope,
          max_slides, motion_mode, slide_on_ceiling, wall_min_slide_angle (node_path:str, ...)
        - setup_collision: Add collision shape (node_path:str, shape:str [2D: rectangle/circle/capsule/segment/custom;
          3D: box/sphere/capsule/cylinder/custom], dimension:str="", width, height, depth, radius,
          ax, ay, bx, by, points:list, disabled:bool, one_way_collision:bool)
        - set_layers: Set collision layer/mask (node_path:str, layer:int=null, mask:int=null)
        - get_layers: Get layer/mask info (node_path:str)
        - collision_info: Get collision shapes (node_path:str, include_children:bool=true)
        - add_raycast: Add RayCast node (node_path:str, target_x:float=0, target_y:float [2D:50/3D:-1],
          target_z:float=0, dimension:str="2d"|"3d", name:str="RayCast", enabled:bool=true,
          collision_mask:int=1, collide_with_areas:bool=false, collide_with_bodies:bool=true, hit_from_inside:bool=false)
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
        - add_mesh: Add MeshInstance3D (parent_path:str=".", mesh_type:str [BoxMesh/SphereMesh/
          CylinderMesh/CapsuleMesh/PlaneMesh/PrismMesh/TorusMesh/QuadMesh], name:str="",
          mesh_file:str="" [res:// .glb/.gltf/.obj], mesh_properties:dict=null)
        - setup_camera: Configure/create Camera3D — flat keys: fov, near, far, size,
          projection, current, cull_mask, environment_path, look_at, rotation, position,
          name, parent_path (node_path:str="" creates a new one)
        - setup_lighting: Add light (light_type:str [DirectionalLight3D/OmniLight3D/SpotLight3D]
          or preset:str [sun/indoor/dramatic], parent_path:str=".", name:str="",
          flat keys: color, energy, shadows, range, attenuation, spot_angle,
          spot_angle_attenuation, rotation, position)
        - setup_environment: Configure/create WorldEnvironment — flat keys: background_mode,
          ambient_light_*, fog_*, glow_*, ssao_*, ssr_*, sdfgi_enabled, tonemap_*;
          plus nested sky:dict{sky_curve, sun_angle_max}
          (node_path:str="" creates a new one)
        - add_gridmap: Add/configure GridMap (parent_path:str=".", name:str="",
          mesh_library_path:str="", node_path:str="", cell_size:dict{x,y,z}, cells:list)
        - set_material: Set StandardMaterial3D — flat keys: albedo_color, albedo_texture,
          metallic, roughness, normal_texture, emission, emission_color, emission_energy,
          transparency, cull_mode, surface_index (node_path:str, ...)
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
        - create: Create particles node (parent_path:str=".", is_3d:bool=false,
          name:str="Particles", flat keys: amount, lifetime, explosiveness,
          randomness, one_shot, emitting)
        - set_material: Set particle material — flat keys: direction, spread, gravity,
          initial_velocity_min/max, angular_velocity_min/max, orbit_velocity_min/max,
          damping_min/max, scale_min/max, color, emission_shape, emission_sphere_radius,
          emission_box_extents, emission_ring_* (node_path:str, ...)
        - set_gradient: Set color gradient (node_path:str, stops:list of {offset:float, color:str})
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
        - setup_region: Add NavigationRegion under a parent (node_path:str=parent, mode:str="auto"|"2d"|"3d",
          flat keys: name, navigation_layers, cell_size, agent_radius; 3D: agent_height,
          agent_max_climb, agent_max_slope, cell_height; 2D: source_geometry_mode)
        - setup_agent: Add NavigationAgent under a parent (node_path:str=parent, mode:str="auto"|"2d"|"3d",
          flat keys: name, radius, max_speed, max_neighbors, neighbor_distance,
          path_desired_distance, target_desired_distance, avoidance_enabled, navigation_layers)
        - bake: Bake navigation mesh (node_path:str, outline:list of [x,y] for 2D)
        - set_layers: Set navigation layers (node_path:str, layers:int bitmask
          OR layer_bits:list of 1-based layer numbers)
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
        - add_player: Add AudioStreamPlayer (node_path:str=parent, name:str [required],
          type:str="AudioStreamPlayer"|"AudioStreamPlayer2D"|"AudioStreamPlayer3D",
          stream:str="" [res:// path], flat keys: volume_db, bus, autoplay, max_distance,
          attenuation, attenuation_model, unit_size)
        - add_bus: Add audio bus (name:str, send:str="Master", volume_db:float, mute:bool, solo:bool, at_position:int=-1)
        - add_effect: Add bus effect (bus:str, effect_type:str [reverb/delay/chorus/distortion/
          eq/compressor/limiter], params:dict [nested, effect-specific], at_position:int=-1)
        - set_bus: Configure bus (name:str, flat keys: volume_db, mute, solo, bypass_effects, send, rename)
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
        - create: Create .tres resource, parent dirs auto-created (path:str, type:str, properties:dict=null, overwrite:bool=false)
        - preview: Get resource thumbnail (path:str, max_size:int=256)
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
        - find_signals: Find signal connections (node_path:str="", signal_name:str="")
        - set_property: Batch set property by type, walks whole scene (type:str, property:str, value:any)
        - find_references: Search whole project for a pattern, max 100 hits (pattern:str)
        - dependencies: Get scene/resource dependencies (path:str [required, no current-scene fallback])
        - cross_scene_set: Set property across scenes (type:str, property:str, value:any,
          path_filter:str="res://" [directory to scan], exclude_addons:bool=true,
          force:bool=false [must be true to write], dry_run:bool=null)
        - script_references: Find script/resource usage (query:str, path:str="res://", include_addons:bool=false)
        - add_nodes: Batch add nodes (nodes:list)
        - circular_deps: Detect circular dependencies (path:str="res://", include_addons:bool=false)
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
        - run_scenario: Run test scenario; keycode input steps auto-release unless auto_release=false (steps:list, scene_path:str="")
        - assert_state: Assert node property (node_path:str, property:str, expected:any, operator:str="eq")
        - assert_text: Assert screen text (text:str, partial:bool=true, case_sensitive:bool=true)
        - compare_screenshots: Compare images (image_a:str, image_b:str,
          threshold:int=10 [per-channel 0-255 tolerance, NOT a similarity ratio])
        - stress_test: Run stress test (duration:float=5.0, actions:list=null)
        - report: Get test report (clear:bool=false)
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
        - export: Export project (preset_name:str="", preset_index:int=-1, debug:bool=true)
        - info: Get export info (no params)
        - list_android: List Android devices (no params)
        - android_info: Get Android preset info (preset_name:str="", preset_index:int=-1)
        - deploy_android: Deploy to Android (device_serial:str="", preset_name:str="",
          preset_index:int=-1, debug:bool=true, launch:bool=true, skip_export:bool=false)
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
        - signal_flow: Map persistent in-scene signal connections, whole scene (no params)
        - unused_resources: Find unused resources (path:str="res://", include_addons:bool=false)
        - statistics: Get project statistics (path:str="res://", include_addons:bool=false)
        - performance: Get RUNNING GAME performance monitors, requires a playing scene (category:str="")
        - editor_performance: Get editor-process performance (no params)
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