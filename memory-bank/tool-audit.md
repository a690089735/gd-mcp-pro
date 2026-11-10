# 工具全量三方对照审计

由 `server/tools_audit.py` 自动生成，请勿手工编辑表格部分。

重新生成：

```
python server/tools_audit.py --md memory-bank/tool-audit.md
```

## 汇总

- commands: 186
- py_missing_tool: 0
- compact_missing: 0
- required_not_sent: 0
- dead: 0
- missing_optional: 0
- doc_gap: 0

## 待处理项（0）

无。

## 全量对照表

| # | 命令 | GD 文件 | 必填 | 可选 | Python 工具 | 紧凑模式 | 状态 |
|---|---|---|---|---|---|---|---|
| 1 | `add_animation_track` | animation_commands.gd | animation, node_path, track_path | track_type, update_mode | `add_animation_track` | `animation.add_track` | OK |
| 2 | `add_audio_bus` | audio_commands.gd | name | at_position, mute, send, solo, volume_db | `add_audio_bus` | `audio.add_bus` | OK |
| 3 | `add_audio_bus_effect` | audio_commands.gd | bus, effect_type | at_position, attack_us, ceiling_db, cutoff_hz, damping, depth, drive, dry, feedback, gain, keep_hf_hz, mix, mode, params, post_gain, pre_gain, range_max_hz, range_min_hz, rate_hz, ratio, release_ms, resonance, room_size, soft_clip_db, soft_clip_ratio, spread, tap1_active, tap1_delay_ms, tap1_level_db, tap2_active, tap2_delay_ms, tap2_level_db, threshold, threshold_db, voice_count, volume_db, wet | `add_audio_bus_effect` | `audio.add_effect` | OK |
| 4 | `add_audio_player` | audio_commands.gd | name, node_path | attenuation, attenuation_model, autoplay, bus, max_distance, stream, type, unit_size, volume_db | `add_audio_player` | `audio.add_player` | OK |
| 5 | `add_autoload` | project_commands.gd | name, path | - | `add_autoload` | `resource.add_autoload` | OK |
| 6 | `add_gridmap` | scene_3d_commands.gd | - | cell_size, cells, mesh_library_path, name, node_path, parent_path | `add_gridmap` | `scene_3d.add_gridmap` | OK |
| 7 | `add_mesh_instance` | scene_3d_commands.gd | - | mesh_file, mesh_properties, mesh_type, name, parent_path | `add_mesh_instance` | `scene_3d.add_mesh` | OK |
| 8 | `add_node` | node_commands.gd | type | name, parent_path, properties | `add_node` | `node.add` | OK |
| 9 | `add_raycast` | physics_commands.gd | node_path | collide_with_areas, collide_with_bodies, collision_mask, dimension, enabled, hit_from_inside, name, target_x, target_y, target_z | `add_raycast` | `physics.add_raycast` | OK |
| 10 | `add_resource` | node_commands.gd | node_path, property, resource_type | resource_properties | `add_resource` | `node.add_resource` | OK |
| 11 | `add_scene_instance` | scene_commands.gd | scene_path | name, parent_path | `add_scene_instance` | `scene.instance` | OK |
| 12 | `add_state_machine_state` | animation_tree_commands.gd | blend_points, node_path, state_name | animation, cyclic_length, position_x, position_y, state_machine_path, state_type, sync, sync_mode | `add_state_machine_state` | `animation.add_state` | OK |
| 13 | `add_state_machine_transition` | animation_tree_commands.gd | from_state, node_path, to_state | advance_expression, advance_mode, state_machine_path, switch_mode, xfade_time | `add_state_machine_transition` | `animation.add_transition` | OK |
| 14 | `add_virtual_joystick` | theme_commands.gd | - | anchor_preset, margin, mode, name, parent_path, visibility | `add_virtual_joystick` | `ui.add_virtual_joystick` | OK |
| 15 | `analyze_scene_complexity` | analysis_commands.gd | - | path | `analyze_scene_complexity` | `diagnostics.scene_complexity` | OK |
| 16 | `analyze_signal_flow` | analysis_commands.gd | - | - | `analyze_signal_flow` | `diagnostics.signal_flow` | OK |
| 17 | `apply_particle_preset` | particle_commands.gd | node_path, preset | - | `apply_particle_preset` | `particles.apply_preset` | OK |
| 18 | `assert_node_state` | test_commands.gd | node_path, property | expected, operator | `assert_node_state` | `test.assert_state` | OK |
| 19 | `assert_screen_text` | test_commands.gd | text | case_sensitive, partial | `assert_screen_text` | `test.assert_text` | OK |
| 20 | `assign_shader_material` | shader_commands.gd | node_path, shader_path | - | `assign_shader_material` | `shader.assign` | OK |
| 21 | `attach_script` | script_commands.gd | node_path, script_path | - | `attach_script` | `script.attach` | OK |
| 22 | `bake_navigation_mesh` | navigation_commands.gd | node_path | outline | `bake_navigation_mesh` | `navigation.bake` | OK |
| 23 | `batch_add_nodes` | batch_commands.gd | - | nodes | `batch_add_nodes` | `batch.add_nodes` | OK |
| 24 | `batch_get_properties` | runtime_commands.gd | - | nodes | `batch_get_properties` | `runtime.batch_get` | OK |
| 25 | `batch_set_property` | batch_commands.gd | property, type | value | `batch_set_property` | `batch.set_property` | OK |
| 26 | `capture_frames` | runtime_commands.gd | - | count, frame_interval, half_resolution | `capture_frames` | `runtime.capture_frames` | OK |
| 27 | `clear_editor_selection` | node_commands.gd | - | - | `clear_editor_selection` | `node.clear_selection` | OK |
| 28 | `clear_output` | editor_commands.gd | - | - | `clear_output` | `editor.clear_output` | OK |
| 29 | `click_button_by_text` | runtime_commands.gd | text | partial | `click_button_by_text` | `runtime.click_button` | OK |
| 30 | `close_script` | script_commands.gd | path | discard_unsaved | `close_script` | `script.close` | OK |
| 31 | `compare_screenshots` | editor_commands.gd | image_a, image_b | threshold | `compare_screenshots` | `test.compare_screenshots` | OK |
| 32 | `connect_signal` | node_commands.gd | method_name, signal_name, source_path, target_path | deferred, one_shot | `connect_signal` | `node.connect_signal` | OK |
| 33 | `create_animation` | animation_commands.gd | name, node_path | length, loop_mode | `create_animation` | `animation.create` | OK |
| 34 | `create_animation_tree` | animation_tree_commands.gd | node_path | anim_player, name | `create_animation_tree` | `animation.create_tree` | OK |
| 35 | `create_particles` | particle_commands.gd | parent_path | amount, emitting, explosiveness, is_3d, lifetime, name, one_shot, randomness | `create_particles` | `particles.create` | OK |
| 36 | `create_resource` | resource_commands.gd | path, type | overwrite, properties | `create_resource` | `resource.create` | OK |
| 37 | `create_scene` | scene_commands.gd | path | force, root_name, root_type | `create_scene` | `scene.create` | OK |
| 38 | `create_script` | script_commands.gd | path | class_name, content, extends, force | `create_script` | `script.create` | OK |
| 39 | `create_shader` | shader_commands.gd | path | content, force, shader_type | `create_shader` | `shader.create` | OK |
| 40 | `create_theme` | theme_commands.gd | path | default_font_size | `create_theme` | `ui.create_theme` | OK |
| 41 | `cross_scene_set_property` | batch_commands.gd | property, type | dry_run, exclude_addons, force, path_filter, value | `cross_scene_set_property` | `batch.cross_scene_set` | OK |
| 42 | `delete_node` | node_commands.gd | node_path | - | `delete_node` | `node.delete` | OK |
| 43 | `delete_scene` | scene_commands.gd | path | - | `delete_scene` | `scene.delete` | OK |
| 44 | `deploy_to_android` | android_commands.gd | - | debug, device_serial, launch, preset_index, preset_name, skip_export | `deploy_to_android` | `export.deploy_android` | OK |
| 45 | `detect_circular_dependencies` | analysis_commands.gd | - | include_addons, path | `detect_circular_dependencies` | `batch.circular_deps` | OK |
| 46 | `disconnect_signal` | node_commands.gd | method_name, signal_name, source_path, target_path | - | `disconnect_signal` | `node.disconnect_signal` | OK |
| 47 | `duplicate_node` | node_commands.gd | node_path | name | `duplicate_node` | `node.duplicate` | OK |
| 48 | `edit_resource` | resource_commands.gd | path | properties | `edit_resource` | `resource.edit` | OK |
| 49 | `edit_script` | script_commands.gd | path | content, end_line, force, insert_at_line, replacements, start_line, text | `edit_script` | `script.edit` | OK |
| 50 | `edit_shader` | shader_commands.gd | path | content, force, replacements | `edit_shader` | `shader.edit` | OK |
| 51 | `execute_editor_script` | editor_commands.gd | code | allow_unsafe_editor_io | `execute_editor_script` | `editor.execute_script` | OK |
| 52 | `execute_game_script` | runtime_commands.gd | code | - | `execute_game_script` | `runtime.execute_script` | OK |
| 53 | `export_patch_pck` | export_commands.gd | output_path | patches, preset_index, preset_name, timeout_sec | `export_patch_pck` | `export.patch_pck` | OK |
| 54 | `export_project` | export_commands.gd | - | debug, preset_index, preset_name | `export_project` | `export.export` | OK |
| 55 | `find_nearby_nodes` | runtime_commands.gd | - | group_filter, max_results, position, radius, type_filter | `find_nearby_nodes` | `runtime.find_nearby` | OK |
| 56 | `find_node_references` | batch_commands.gd | pattern | - | `find_node_references` | `batch.find_references` | OK |
| 57 | `find_nodes_by_script` | runtime_commands.gd | script | properties | `find_nodes_by_script` | `runtime.find_by_script` | OK |
| 58 | `find_nodes_by_type` | batch_commands.gd | type | recursive | `find_nodes_by_type` | `batch.find_by_type` | OK |
| 59 | `find_nodes_in_group` | node_commands.gd | group | - | `find_nodes_in_group` | `node.find_in_group` | OK |
| 60 | `find_script_references` | analysis_commands.gd | query | include_addons, path | `find_script_references` | `batch.script_references` | OK |
| 61 | `find_signal_connections` | batch_commands.gd | - | node_path, signal_name | `find_signal_connections` | `batch.find_signals` | OK |
| 62 | `find_ui_elements` | runtime_commands.gd | - | type_filter | `find_ui_elements` | `runtime.find_ui` | OK |
| 63 | `find_unused_resources` | analysis_commands.gd | - | include_addons, path | `find_unused_resources` | `diagnostics.unused_resources` | OK |
| 64 | `get_android_preset_info` | android_commands.gd | - | preset_index, preset_name | `get_android_preset_info` | `export.android_info` | OK |
| 65 | `get_animation_info` | animation_commands.gd | animation, node_path | - | `get_animation_info` | `animation.info` | OK |
| 66 | `get_animation_tree_structure` | animation_tree_commands.gd | node_path | - | `get_animation_tree_structure` | `animation.tree_structure` | OK |
| 67 | `get_audio_bus_layout` | audio_commands.gd | - | - | `get_audio_bus_layout` | `audio.bus_layout` | OK |
| 68 | `get_audio_info` | audio_commands.gd | node_path | - | `get_audio_info` | `audio.info` | OK |
| 69 | `get_autoload` | runtime_commands.gd | name | properties | `get_autoload` | `runtime.get_autoload` | OK |
| 70 | `get_collision_info` | physics_commands.gd | node_path | include_children | `get_collision_info` | `physics.collision_info` | OK |
| 71 | `get_editor_camera` | editor_commands.gd | - | - | `get_editor_camera` | `editor.get_camera` | OK |
| 72 | `get_editor_errors` | editor_commands.gd | - | max_lines | `get_editor_errors` | `editor.errors` | OK |
| 73 | `get_editor_performance` | profiling_commands.gd | - | - | `get_editor_performance` | `diagnostics.editor_performance` | OK |
| 74 | `get_editor_screenshot` | editor_commands.gd | - | save_path | `get_editor_screenshot` | `editor.editor_screenshot` | OK |
| 75 | `get_editor_selection` | node_commands.gd | - | top_only | `get_editor_selection` | `node.get_selection` | OK |
| 76 | `get_export_info` | export_commands.gd | - | - | `get_export_info` | `export.info` | OK |
| 77 | `get_filesystem_tree` | project_commands.gd | - | filter, max_depth, path | `get_filesystem_tree` | `project.tree` | OK |
| 78 | `get_game_node_properties` | runtime_commands.gd | node_path | properties | `get_game_node_properties` | `runtime.get_properties` | OK |
| 79 | `get_game_scene_tree` | runtime_commands.gd | - | max_depth, named_only, script_filter, type_filter | `get_game_scene_tree` | `runtime.game_tree` | OK |
| 80 | `get_game_screenshot` | editor_commands.gd | - | save_path | `get_game_screenshot` | `editor.game_screenshot` | OK |
| 81 | `get_godot_executable` | headless_commands.gd | - | - | `get_godot_executable` | `headless.executable` | OK |
| 82 | `get_gridmap_info` | scene_3d_commands.gd | node_path | bounds, include_octants, item, list_cells, max_cells, max_octants | `get_gridmap_info` | `scene_3d.gridmap_info` | OK |
| 83 | `get_input_actions` | input_map_commands.gd | - | filter, include_builtin | `get_input_actions` | `input.get_actions` | OK |
| 84 | `get_navigation_info` | navigation_commands.gd | node_path | - | `get_navigation_info` | `navigation.info` | OK |
| 85 | `get_node_groups` | node_commands.gd | node_path | - | `get_node_groups` | `node.get_groups` | OK |
| 86 | `get_node_properties` | node_commands.gd | node_path | category | `get_node_properties` | `node.get_properties` | OK |
| 87 | `get_open_scripts` | script_commands.gd | - | - | `get_open_scripts` | `script.open_scripts` | OK |
| 88 | `get_output_log` | editor_commands.gd | - | filter, max_lines | `get_output_log` | `editor.output_log` | OK |
| 89 | `get_particle_info` | particle_commands.gd | node_path | - | `get_particle_info` | `particles.info` | OK |
| 90 | `get_performance_monitors` | profiling_commands.gd | - | category | `get_performance_monitors` | `diagnostics.performance` | OK |
| 91 | `get_physics_layers` | physics_commands.gd | node_path | - | `get_physics_layers` | `physics.get_layers` | OK |
| 92 | `get_project_info` | project_commands.gd | - | - | `get_project_info` | `project.info` | OK |
| 93 | `get_project_settings` | project_commands.gd | - | key, non_default_only, section | `get_project_settings` | `project.get_settings` | OK |
| 94 | `get_project_statistics` | analysis_commands.gd | - | include_addons, path | `get_project_statistics` | `diagnostics.statistics` | OK |
| 95 | `get_resource_preview` | resource_commands.gd | path | max_size | `get_resource_preview` | `resource.preview` | OK |
| 96 | `get_scene_dependencies` | batch_commands.gd | path | - | `get_scene_dependencies` | `batch.dependencies` | OK |
| 97 | `get_scene_exports` | scene_commands.gd | path | - | `get_scene_exports` | `scene.exports` | OK |
| 98 | `get_scene_file_content` | scene_commands.gd | path | - | `get_scene_file_content` | `scene.file_content` | OK |
| 99 | `get_scene_tree` | scene_commands.gd | - | max_depth | `get_scene_tree` | `scene.tree` | OK |
| 100 | `get_shader_params` | shader_commands.gd | node_path | - | `get_shader_params` | `shader.get_params` | OK |
| 101 | `get_signals` | editor_commands.gd | node_path | - | `get_signals` | `editor.get_signals` | OK |
| 102 | `get_test_report` | test_commands.gd | - | clear | `get_test_report` | `test.report` | OK |
| 103 | `get_theme_info` | theme_commands.gd | node_path | - | `get_theme_info` | `ui.theme_info` | OK |
| 104 | `get_unsaved_state` | editor_commands.gd | - | - | `get_unsaved_state` | `editor.unsaved_state` | OK |
| 105 | `list_android_devices` | android_commands.gd | - | - | `list_android_devices` | `export.list_android` | OK |
| 106 | `list_animations` | animation_commands.gd | node_path | - | `list_animations` | `animation.list` | OK |
| 107 | `list_export_presets` | export_commands.gd | - | - | `list_export_presets` | `export.list_presets` | OK |
| 108 | `list_scripts` | script_commands.gd | - | path, recursive | `list_scripts` | `script.list` | OK |
| 109 | `monitor_properties` | runtime_commands.gd | node_path | frame_count, frame_interval, properties | `monitor_properties` | `runtime.monitor` | OK |
| 110 | `move_node` | node_commands.gd | new_parent_path, node_path | - | `move_node` | `node.move` | OK |
| 111 | `move_to` | runtime_commands.gd | - | arrival_radius, camera_path, look_at_target, player_path, run, target, timeout | `move_to` | `runtime.move_to` | OK |
| 112 | `navigate_to` | runtime_commands.gd | - | camera_path, move_speed, player_path, target | `navigate_to` | `runtime.navigate_to` | OK |
| 113 | `open_scene` | scene_commands.gd | path | - | `open_scene` | `scene.open` | OK |
| 114 | `play_scene` | scene_commands.gd | - | mode | `play_scene` | `scene.play` | OK |
| 115 | `project_path_to_uid` | project_commands.gd | path | - | `project_path_to_uid` | `project.path_to_uid` | OK |
| 116 | `read_resource` | resource_commands.gd | path | force | `read_resource` | `resource.read` | OK |
| 117 | `read_script` | script_commands.gd | path | - | `read_script` | `script.read` | OK |
| 118 | `read_shader` | shader_commands.gd | path | - | `read_shader` | `shader.read` | OK |
| 119 | `reload_open_scripts` | script_commands.gd | - | discard_unsaved | `reload_open_scripts` | `script.reload_open` | OK |
| 120 | `reload_plugin` | editor_commands.gd | - | - | `reload_plugin` | `editor.reload_plugin` | OK |
| 121 | `reload_project` | editor_commands.gd | - | - | `reload_project` | `editor.reload_project` | OK |
| 122 | `remove_animation` | animation_commands.gd | name, node_path | - | `remove_animation` | `animation.remove` | OK |
| 123 | `remove_autoload` | project_commands.gd | name | - | `remove_autoload` | `resource.remove_autoload` | OK |
| 124 | `remove_state_machine_state` | animation_tree_commands.gd | node_path, state_name | state_machine_path | `remove_state_machine_state` | `animation.remove_state` | OK |
| 125 | `remove_state_machine_transition` | animation_tree_commands.gd | from_state, node_path, to_state | state_machine_path | `remove_state_machine_transition` | `animation.remove_transition` | OK |
| 126 | `rename_node` | node_commands.gd | new_name, node_path | - | `rename_node` | `node.rename` | OK |
| 127 | `replay_recording` | runtime_commands.gd | events | speed | `replay_recording` | `runtime.replay` | OK |
| 128 | `run_headless_scene` | headless_commands.gd | scene_path | args, quit_after_frames, timeout_sec | `run_headless_scene` | `headless.run_scene` | OK |
| 129 | `run_headless_script` | headless_commands.gd | script_path | args, quit_after_frames, timeout_sec | `run_headless_script` | `headless.run_script` | OK |
| 130 | `run_stress_test` | test_commands.gd | - | actions, duration | `run_stress_test` | `test.stress_test` | OK |
| 131 | `run_test_scenario` | test_commands.gd | - | scene_path, steps | `run_test_scenario` | `test.run_scenario` | OK |
| 132 | `save_all` | editor_commands.gd | - | scenes, scripts | `save_all` | `editor.save_all` | OK |
| 133 | `save_scene` | scene_commands.gd | - | path | `save_scene` | `scene.save` | OK |
| 134 | `search_files` | project_commands.gd | query | file_type, max_results, path | `search_files` | `project.search` | OK |
| 135 | `search_in_files` | project_commands.gd | query | file_type, include_addons, max_results, path, regex | `search_in_files` | `project.search_content` | OK |
| 136 | `select_nodes` | node_commands.gd | node_path | focus, for_property, inspect, inspector_only, mode, node_paths | `select_nodes` | `node.select` | OK |
| 137 | `set_anchor_preset` | node_commands.gd | node_path, preset | keep_offsets | `set_anchor_preset` | `node.set_anchor` | OK |
| 138 | `set_animation_keyframe` | animation_commands.gd | animation, node_path | easing, time, track_index, value | `set_animation_keyframe` | `animation.set_keyframe` | OK |
| 139 | `set_audio_bus` | audio_commands.gd | name | bypass_effects, mute, rename, send, solo, volume_db | `set_audio_bus` | `audio.set_bus` | OK |
| 140 | `set_auto_dismiss` | editor_commands.gd | - | enabled | `set_auto_dismiss` | `editor.auto_dismiss` | OK |
| 141 | `set_blend_tree_node` | animation_tree_commands.gd | blend_points, blend_tree_state, bt_node_name, bt_node_type, node_path | abort_on_reset, animation, connect_port, connect_to, cyclic_length, position_x, position_y, state_machine_path, sync, sync_mode | `set_blend_tree_node` | `animation.set_blend_node` | OK |
| 142 | `set_editor_camera` | editor_commands.gd | - | fov, look_at, position, rotation_degrees | `set_editor_camera` | `editor.set_camera` | OK |
| 143 | `set_game_node_property` | runtime_commands.gd | node_path, property | value | `set_game_node_property` | `runtime.set_property` | OK |
| 144 | `set_game_speed` | test_commands.gd | - | scale | `set_game_speed` | `test.game_speed` | OK |
| 145 | `set_input_action` | input_map_commands.gd | action | deadzone, events | `set_input_action` | `input.define` | OK |
| 146 | `set_material_3d` | scene_3d_commands.gd | node_path | albedo_texture, cull_mode, emission, emission_color, emission_energy, emission_texture, metallic, metallic_texture, normal_texture, roughness, roughness_texture, surface_index, transparency | `set_material_3d` | `scene_3d.set_material` | OK |
| 147 | `set_navigation_layers` | navigation_commands.gd | node_path | layer_bits, layer_names, layers | `set_navigation_layers` | `navigation.set_layers` | OK |
| 148 | `set_node_groups` | node_commands.gd | node_path | groups | `set_node_groups` | `node.set_groups` | OK |
| 149 | `set_particle_color_gradient` | particle_commands.gd | node_path | stops | `set_particle_color_gradient` | `particles.set_gradient` | OK |
| 150 | `set_particle_material` | particle_commands.gd | node_path | angular_velocity_max, angular_velocity_min, attractor_interaction_enabled, color, damping_max, damping_min, direction, emission_box_extents, emission_ring_height, emission_ring_inner_radius, emission_ring_radius, emission_shape, emission_sphere_radius, gravity, initial_velocity_max, initial_velocity_min, orbit_velocity_max, orbit_velocity_min, scale_max, scale_min, spread | `set_particle_material` | `particles.set_material` | OK |
| 151 | `set_physics_layers` | physics_commands.gd | node_path | collision_layer, collision_mask | `set_physics_layers` | `physics.set_layers` | OK |
| 152 | `set_project_setting` | project_commands.gd | key | type, value | `set_project_setting` | `project.set_setting` | OK |
| 153 | `set_shader_param` | shader_commands.gd | node_path, param | value | `set_shader_param` | `shader.set_param` | OK |
| 154 | `set_theme_color` | theme_commands.gd | color, name, node_path | theme_type | `set_theme_color` | `ui.set_color` | OK |
| 155 | `set_theme_constant` | theme_commands.gd | name, node_path | value | `set_theme_constant` | `ui.set_constant` | OK |
| 156 | `set_theme_font_size` | theme_commands.gd | name, node_path | size | `set_theme_font_size` | `ui.set_font_size` | OK |
| 157 | `set_theme_stylebox` | theme_commands.gd | name, node_path | bg_color, border_color, border_width, corner_radius, padding | `set_theme_stylebox` | `ui.set_stylebox` | OK |
| 158 | `set_tree_parameter` | animation_tree_commands.gd | node_path, parameter | value | `set_tree_parameter` | `animation.set_param` | OK |
| 159 | `setup_camera_3d` | scene_3d_commands.gd | - | cull_mask, current, environment_path, far, fov, look_at, name, near, node_path, parent_path, projection, rotation, size | `setup_camera_3d` | `scene_3d.setup_camera` | OK |
| 160 | `setup_collision` | physics_commands.gd | node_path, shape | ax, ay, bx, by, depth, dimension, disabled, height, one_way_collision, points, radius, width | `setup_collision` | `physics.setup_collision` | OK |
| 161 | `setup_control` | theme_commands.gd | node_path | anchor_preset, grow_h, grow_v, margins, max_size, min_size, offset_transform, pivot_offset_ratio, separation, size_flags_h, size_flags_v | `setup_control` | `ui.setup_control` | OK |
| 162 | `setup_environment` | scene_3d_commands.gd | - | ambient_light_color, ambient_light_energy, ambient_light_source, background_mode, fog_density, fog_enabled, fog_light_color, fog_light_energy, glow_bloom, glow_enabled, glow_intensity, glow_strength, name, node_path, parent_path, sdfgi_enabled, sky, sky_curve, ssao_enabled, ssao_intensity, ssao_radius, ssr_enabled, ssr_fade_in, ssr_fade_out, ssr_max_steps, sun_angle_max, tonemap_exposure, tonemap_mode, tonemap_white | `setup_environment` | `scene_3d.setup_environment` | OK |
| 163 | `setup_ik_modifier` | animation_tree_commands.gd | settings, skeleton_path | active, angular_delta_limit, deterministic, ik_type, influence, max_iterations, min_distance, mutable_bone_axes, name | `setup_ik_modifier` | `animation.setup_ik` | OK |
| 164 | `setup_lighting` | scene_3d_commands.gd | - | area_attenuation, area_normalize_energy, area_range, area_size, area_texture, attenuation, energy, light_type, name, parent_path, preset, range, rotation, shadows, spot_angle, spot_angle_attenuation | `setup_lighting` | `scene_3d.setup_lighting` | OK |
| 165 | `setup_navigation_agent` | navigation_commands.gd | node_path | avoidance_enabled, max_neighbors, max_speed, mode, name, navigation_layers, neighbor_distance, path_desired_distance, radius, target_desired_distance | `setup_navigation_agent` | `navigation.setup_agent` | OK |
| 166 | `setup_navigation_region` | navigation_commands.gd | node_path | agent_height, agent_max_climb, agent_max_slope, agent_radius, cell_height, cell_size, mode, name, navigation_layers, source_geometry_mode | `setup_navigation_region` | `navigation.setup_region` | OK |
| 167 | `setup_physics_body` | physics_commands.gd | node_path | angular_damp, contact_monitor, continuous_cd, floor_max_angle, floor_snap_length, floor_stop_on_slope, freeze, freeze_mode, gravity_scale, linear_damp, mass, max_contacts_reported, max_slides, motion_mode, physics_material_override, slide_on_ceiling, wall_min_slide_angle | `setup_physics_body` | `physics.setup_body` | OK |
| 168 | `simulate_action` | input_commands.gd | action | pressed, strength | `simulate_action` | `input.simulate` | OK |
| 169 | `simulate_key` | input_commands.gd | keycode | alt, ctrl, hold_sec, pressed, shift | `simulate_key` | `input.key` | OK |
| 170 | `simulate_mouse_click` | input_commands.gd | - | auto_release, button, double_click, pressed, x, y | `simulate_mouse_click` | `input.mouse_click` | OK |
| 171 | `simulate_mouse_move` | input_commands.gd | - | button_mask, relative_x, relative_y, unhandled, x, y | `simulate_mouse_move` | `input.mouse_move` | OK |
| 172 | `simulate_sequence` | input_commands.gd | - | events, frame_delay | `simulate_sequence` | `input.sequence` | OK |
| 173 | `start_recording` | runtime_commands.gd | - | - | `start_recording` | `runtime.start_recording` | OK |
| 174 | `stop_recording` | runtime_commands.gd | - | - | `stop_recording` | `runtime.stop_recording` | OK |
| 175 | `stop_scene` | scene_commands.gd | - | - | `stop_scene` | `scene.stop` | OK |
| 176 | `tilemap_clear` | tilemap_commands.gd | node_path | layer | `tilemap_clear` | `tilemap.clear` | OK |
| 177 | `tilemap_fill_rect` | tilemap_commands.gd | node_path | alternative, atlas_x, atlas_y, layer, source_id, x1, x2, y1, y2 | `tilemap_fill_rect` | `tilemap.fill_rect` | OK |
| 178 | `tilemap_get_cell` | tilemap_commands.gd | node_path | layer, x, y | `tilemap_get_cell` | `tilemap.get_cell` | OK |
| 179 | `tilemap_get_info` | tilemap_commands.gd | node_path | - | `tilemap_get_info` | `tilemap.info` | OK |
| 180 | `tilemap_get_used_cells` | tilemap_commands.gd | node_path | layer, max_count | `tilemap_get_used_cells` | `tilemap.used_cells` | OK |
| 181 | `tilemap_set_cell` | tilemap_commands.gd | node_path | alternative, atlas_x, atlas_y, layer, source_id, x, y | `tilemap_set_cell` | `tilemap.set_cell` | OK |
| 182 | `uid_to_project_path` | project_commands.gd | uid | - | `uid_to_project_path` | `project.uid_to_path` | OK |
| 183 | `update_property` | node_commands.gd | node_path, property | value | `update_property` | `node.update_property` | OK |
| 184 | `validate_script` | script_commands.gd | path | - | `validate_script` | `script.validate` | OK |
| 185 | `wait_for_node` | runtime_commands.gd | node_path | poll_frames, timeout | `wait_for_node` | `runtime.wait_for_node` | OK |
| 186 | `watch_signals` | runtime_commands.gd | - | duration_ms, node_paths, signal_filter | `watch_signals` | `runtime.watch_signals` | OK |

