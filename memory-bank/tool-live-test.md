# 全量工具实机测试记录

对象：Godot 4.7-beta3（official），测试项目 `E:/Godot-MCP-Test/`，插件 v1.15.1。
方式：**逐个调用具名 MCP 工具**（而非 `batch_execute` 透传），并对写入类工具**回读校验**。

> ⚠ 方法论教训：`batch_execute` 直接把原始命令发给 GDScript，会**绕过 Python 的参数
> 转换层**。用它测试会得出错误结论（例如 `edit_script` 的 search/replace 会假失败）。
> 逐工具测试必须使用具名工具。

## 结论汇总

| 批次 | 类别 | 结果 |
|---|---|---|
| 1 | 项目/文件系统 (8) | 通过；发现 `file_type`/`filter` 语义缺陷（已修） |
| 2 | 场景 (10) | 10/10 通过 |
| 3 | 节点 (17) | 通过；`category` 语义为属性名前缀（已补文档） |
| 4 | 脚本 (7) | 7/7 通过（含 search/replace、行插入、行区间三种模式） |
| 5 | 编辑器 (12) | 通过；`set_editor_camera` 旋转完全失效（已修） |
| 6 | 输入 (7) | 7/7 通过 |
| 7 | 运行时 (19) | 19/19 通过 |
| 8 | 动画 (14) | 14/14 通过（含 AnimationTree 状态机 + BlendTree 全系列） |
| 9 | TileMap (6) + UI (7) | TileMap 6/6；UI 7/7（`setup_control` 已修并复测通过） |
| 10 | 物理 (6) | 6/6 通过 |
| 11 | 3D (6) | 6/6 通过 |
| 12 | 粒子 (5) + 导航 (5) | 粒子 5/5；导航 4/5（`bake_navigation_mesh` 见下） |
| 13 | 音频 (6) | 6/6 通过（含嵌套 `params` 例外） |
| 14 | 着色器 (6) + 资源 (6) | 12/12 通过 |
| 15 | 批量/分析 (9) | 9/9（`cross_scene_set_property` 已修并复测通过） |
| 16 | 导出/诊断 (6) | 6/6 通过（无导出预设/无 ADB 时降级提示正确） |

## 本轮发现并修复的真实缺陷（6 个）

1. **`search_files` / `search_in_files` 的 `file_type`** — GDScript 用
   `get_extension()` 比较（返回不带点的 `gd`），文档却写 `".gd"`，导致带点写法
   **永远 0 命中**。Python 侧新增 `_bare_extension()` 归一化。
2. **`get_filesystem_tree` 的 `filter`** — 实际是 `String.match()` glob（`*.gd`），
   文档写成"扩展名"。新增 `_glob_pattern()` 归一化。
3. **`set_editor_camera`** — Python 发 `rotation`/`distance`，GDScript 读
   `rotation_degrees`/`look_at`/`fov`。**旋转完全无效**，`distance` 是死参数。
4. **`set_physics_layers`** — Python 发 `layer`/`mask`，GDScript 读
   `collision_layer`/`collision_mask`。**整个工具完全无效**。
5. **`setup_control`** — Python 发 `min_size_x`/`min_size_y`/`theme_path`，
   GDScript 读 `min_size`（`"Vector2(w,h)"` 字符串，用 `Expression` 解析）且无
   `theme_path`；同时 `grow_h`/`grow_v`/`margins`/`separation` 从未暴露。
6. **`cross_scene_set_property`** — Python 发 `scene_paths`（死参数），GDScript
   实际用 `path_filter`（目录）+ `exclude_addons`。

另修正 3 处误导性文档：`get_node_properties.category`、
`execute_editor_script`（必须用 `_mcp_print` 才能拿到 `output`，普通 `print`
只进输出面板）、`run_test_scenario.name`（死参数，已删）。

## 已知上游问题（不修改 `addons/`）

- **`bake_navigation_mesh` 会冻结编辑器**：`navigation_commands.gd` 使用了
  Godot 4.x 已废弃的 `NavigationPolygon.make_polygons_from_outlines()`。在
  4.7-beta3 上该调用阻塞主线程，30s 后 WebSocket 断连，需重启编辑器。
  Python 侧已把超时提到 120s 并在 docstring 中标注风险，但**根因在上游插件**。
- 编辑器日志中大量 `progress_dialog.cpp` 报错是引擎在 `call_deferred` 中使用
  进度对话框的告警，与本项目无关。

## 关键回读校验（证明"成功"不是假成功）

- `setup_physics_body(properties={floor_max_angle, max_slides})` → 节点上读回
  `0.8999999` / `7`
- `add_raycast(properties={collision_mask: 5, collide_with_areas: true})` →
  读回 `collision_mask=5`、`collide_with_areas=true`（默认为 false）
- `add_mesh_instance(properties={radius: 0.75, radial_segments: 32})` →
  `mesh.radius=0.75`、`mesh.radial_segments=32`
- `tilemap_fill_rect(x=2,y=3,width=3,height=2)` → `x1..x2=2..4`、`y1..y2=3..4`，
  6 格，边界格 (4,4) 存在（闭区间语义正确）
- `set_particle_color_gradient(4 色)` → offsets `0 / 0.333 / 0.667 / 1.0`，无多余停靠点
- `set_navigation_layers(layer_numbers=[1,3,5])` → `navigation_layers=21`
- `create_animation(loop_mode=2)` → 回读 `loop_mode=2`（pingpong）
- **输入→物理闭环**：`simulate_action("move_right")` +
  `monitor_properties` → 角色 x 从 2.54 递增到 7.43，velocity 趋近设定的 12.5
- **鼠标→游戏逻辑闭环**：`simulate_mouse_click` 触发 `_shoot()`，
  `find_nodes_by_script("bullet.gd")` 找到新生成的子弹，direction 与点击位置一致
- `move_to({x:0,z:0})` → 1.24s 内从 7.43 走到 0.38

## 审计脚本强化

`test_param_sync.py` 原先把「payload 由局部变量条件构建」的命令整体豁免 MISSING
检查，且 DEAD 检查也一并失效——**55 个命令（32%）处于盲区**，`set_editor_camera`
正是漏网证据。现已解析 `params["key"] = ...` 形式的条件赋值（含 `AnnAssign`），
盲区从 55 降到 15，且 DEAD 检查对全部 174 个命令生效。

新增白名单（附原因）：
- `add_audio_bus_effect`：效果参数读自**嵌套** `params["params"]`
- `set_navigation_layers`：`layer_names` 需项目自定义层名，MCP 层无法解析

## 测试产物清理

已全部删除：`res://_mcp_audit/`（场景/脚本/着色器/主题/资源/截图）、
输入动作 `audit_jump`、音频总线 `AuditBus2`。`reload_project` +
`get_filesystem_tree` 确认项目恢复原状。

## 复测轮次（重启 Godot 后）

上一轮末尾因 `bake_navigation_mesh` 冻结编辑器而断连，6 个修复项当时只有
静态验证。重启后逐一实机复测，**6/6 全部通过**：

| 工具 | 输入 | 回读结果 | 判定 |
|---|---|---|---|
| `search_in_files` | `file_type="*.gd"` | 3 条匹配（bullet/camera_follow/player） | ✅ 带点/带星写法已归一化 |
| `get_filesystem_tree` | `filter="gd"`（裸扩展名） | 3 个 `.gd` 文件 | ✅ 已展开为 `*.gd` |
| `set_editor_camera` | `rotation={-35,45,0}`, `fov=55` | `rotation_degrees={-35,45,0}`、`fov=55` | ✅ 旋转恢复有效 |
| `set_editor_camera` | `position={0,5,10}` + `look_at={0,0,0}`（同时给了零 rotation） | `rotation_degrees.x=-26.565`（= -atan(5/10)） | ✅ `look_at` 正确覆盖 `rotation` |
| `set_physics_layers` | `layer=[1,3]`（1-based 列表）、`mask=12`（位掩码） | `collision_layer=5`、`collision_mask=12`（层 3+4）；`get_physics_layers` 独立回读一致 | ✅ 两种格式均可，工具从"完全失效"恢复 |
| `setup_control` | `margins={12,14,16,18}`, `grow_h/grow_v` | `get_theme_info` → 4 个 `margin_*` 常量全部写入 | ✅ |
| `setup_control` | `min_size_x=220, min_size_y=140`, `size_flags_*`, `separation=17` | `custom_minimum_size=(220,140)`；`size_flags_h=3`(fill_expand)、`size_flags_v=4`(shrink_center)、`separation=17` 且 `has_theme_constant_override=true` | ✅ Vector2 字符串被 `Expression` 正确解析 |
| `cross_scene_set_property` | `path_filter="res://_mcp_audit"`（默认 dry-run） | 仅列出沙盒内 1 个 Button，活动场景标记 `skipped_open_scenes` | ✅ `path_filter` 生效，未误扫全项目 |
| `cross_scene_set_property` | 同上 + `force=true` | 离线场景 `offline_saved`、活动场景 `live_open_scene`；`.tscn` 内搜到 `text = "RetestOK"`，活动节点回读 `text=RetestOK` | ✅ 双路径均真实写入 |

复测沙盒 `res://_mcp_audit/retest.tscn` 与上轮遗留的 `audit_2d.tscn`、
`audit_root.gd(.uid)`、`themes/audit.tres` 已一并删除，`_mcp_audit` 目录
`dir_exists=false`，`reload_project` 确认项目干净。

仍未实机覆盖：`export_project` / `deploy_to_android`（测试项目无导出预设、
未安装 ADB），以及 `bake_navigation_mesh`（上游冻结缺陷，刻意不再触发）。
