# 项目进度

## 已完成 ✅

### 全量实机逐一测试（第十二阶段）
- [x] 新增 `server/tools_audit.py`，生成 GDScript/Python/紧凑模式**三方对照表**
- [x] `memory-bank/tool-audit.md`（174 行自动生成对照表）
- [x] `memory-bank/tool-live-test.md`（16 批次实机记录 + 回读校验证据）
- [x] **174 个工具全部逐一实机调用**，写入类工具回读校验
- [x] 又修 6 个真实缺陷：`file_type`(×2 工具)、`filter`、`set_editor_camera`、
      `set_physics_layers`（整个工具原本完全无效）、`setup_control`、
      `cross_scene_set_property`
- [x] 修正 3 处误导文档：`get_node_properties.category`、
      `execute_editor_script`（需 `_mcp_print`）、删除 `run_test_scenario.name` 死参数
- [x] **加强审计脚本**：原先 55 个命令（32%）因条件构建 payload 而处于 DEAD 检查
      盲区，现已解析 `params["key"]=...` 赋值，盲区降至 15
- [x] 记录上游缺陷：`bake_navigation_mesh` 用了废弃的
      `make_polygons_from_outlines()`，在 4.7-beta3 上冻结编辑器直至断连

### Python Server 核心实现
- [x] 从 Node.js/TypeScript 完整迁移为 Python FastMCP 实现
- [x] 22 个工具模块全部实现（`tools/*.py`）
- [x] WebSocket bridge 实现（`bridge.py`）
- [x] JSON-RPC 2.0 通信协议
- [x] FastMCP 工具注册框架（`server.py`）

### 工具对齐审计
- [x] Python 工具函数与 GDScript 命令一一对应（最终确认 174:174）
- [x] 修复 `android.py` 的 3 个命令名不匹配
- [x] 补齐 10 个缺失的工具暴露
- [x] 删除 2 个无 GDScript 后端的幽灵工具（`collision_layer_info`/`collision_mask_info`）

### v1.13.x 适配
- [x] 心跳保活：Python 端每 10s 发送 JSON-RPC ping
- [x] 端口重试：bind 失败时自动尝试 6505-6514
- [x] 接收端 ping/pong 处理（Godot 发来的 ping 正确回复 pong）

### v1.14.0 上游合并 + Python 适配
- [x] 通过 PR #2 合并上游 v1.14.0（GDScript 端安全性大修）
- [x] `create_script`/`edit_script` 添加 `force` 参数
- [x] `create_shader`/`edit_shader` 添加 `force` 参数
- [x] `cross_scene_set_property` 添加 `dry_run`/`force` 参数
- [x] `execute_editor_script` 添加 `allow_unsafe_editor_io` 参数
- [x] `edit_script` 重写参数构建：`search`/`replace` → `replacements` 数组，`line`/`insert` → `insert_at_line`/`text`
- [x] `edit_shader` 重写参数构建：`search`/`replace` → `replacements` 数组
- [x] 新增 `edit_script` 的 `start_line`/`end_line` 行范围替换支持

### v1.14.1 上游合并 + 全面参数审计
- [x] 通过 PR #3 合并上游 v1.14.1（恢复 `assert_node_state` 游戏端处理器）
- [x] 全面交叉审计：22 个 Python 工具文件 vs 26 个 GDScript 命令文件
- [x] 修复 `assert_node_state`（test.py）：`assertions: dict` → `property` + `expected` + `operator`
- [x] 修复 `connect_signal`（node.py）：`node_path` → `source_path`，`method` → `method_name`
- [x] 修复 `disconnect_signal`（node.py）：同上
- [x] 补充 `run_test_scenario`（test.py）：添加 `scene_path` 可选参数
- [x] 补充 `assert_screen_text`（test.py）：添加 `partial` + `case_sensitive` 可选参数

### v1.15.0 上游合并 + Python 适配
- [x] 合并 upstream v1.15.0（6 个提交：editor selection tools + legacy TileMap support）
- [x] 解决 README.md 合并冲突（工具数 173→175，采用 upstream 版本）
- [x] `node.py` 新增 3 个编辑器选择工具：`get_editor_selection`、`select_nodes`、`clear_editor_selection`
- [x] `tilemap.py` 给 4 个工具添加 `layer` 参数（兼容已弃用的 TileMap 多层节点）
- [x] `physics.py` 删除 2 个无 GDScript 后端的幽灵工具
- [x] 精确工具数量对齐确认：**174 Python : 174 GDScript**
- [x] 新增 `batch_execute` 纯 Python 工具（顺序批量执行，不需要 GDScript 配合）
- [x] 最终工具数：**175 Python**（174 对应 GDScript + 1 纯 Python `batch_execute`）

### 端口绑定稳定性修复
- [x] 诊断间歇性 `OSError 10048`（端口已被占用）
- [x] 修复：`server.py` 始终启用 `port_retry=True`，多个 Cline 实例可共存

### 紧凑模式(--compact)
- [x] 设计方案：175 工具按领域合并为 21 个伞工具 + batch_execute = 22 tools
- [x] 实现 `compact.py`：纯 Python 分发层，通过 ACTION_MAP 映射到 GDScript 命令
- [x] 修改 `server.py`：`--compact` 参数检测 + 条件注册
- [x] 命名优化：`input` 工具的 `action`→`simulate`、`set_action`→`define`（避免二义性）
- [x] 完整类型标注：docstring 使用 `name:type=default` 格式
- [x] 验证：22 tools、174:174 命令映射、完整模式无副作用
- [x] `--compact` 使用 `while` 循环清理（支持多次出现）

### v1.15.1 上游合并 + Python 适配
- [x] 合并 upstream `c17a182`（v1.15.1，15 个 bug 修复），**零冲突**
- [x] 确认 `addons/` 与 `CHANGELOG.md` 与 upstream 完全一致（`git diff` 为空）
- [x] `node.py` → `connect_signal` 新增 `deferred` / `one_shot` 可选参数（对应 GDScript 的 `CONNECT_DEFERRED`/`CONNECT_ONE_SHOT`）
- [x] `profiling.py` → `get_performance_monitors` docstring 说明需先 `play_scene`
- [x] `test.py` → `run_test_scenario` docstring 补全 step 结构与 `auto_release`
- [x] `compact.py` → `scene.tree` / `node.connect_signal` / `test.run_scenario` / `diagnostics.performance` action 说明同步
- [x] 映射校验：GDScript 174 : 完整模式 174 : 紧凑 ACTION_MAP 174，PASS
- [x] 全量 Python 语法检查通过

### 参数级对齐大修（v1.15.1 之后）
- [x] 写 AST + GDScript 递归解析的参数审计脚本，发现 174:174 工具对齐是「假的安全感」
- [x] 阶段1：修复 11 个 P0 硬故障（`require_*` 必填参数名不匹配 → 调用必然报错）
- [x] 阶段2：修复 18 处 `properties` 包装失效（改传输层平铺，工具签名不变）
- [x] 阶段3：修复 14 处参数名/结构不一致（含 `play_scene` custom 模式、`tilemap_fill_rect` 只填 1 格）
- [x] 阶段4：补齐 24 处 GDScript 支持但未暴露的可选参数
- [x] 阶段5：清理 7 处 GDScript 从不读取的无效参数
- [x] 阶段6：审计固化为 `server/tests/`（`test_param_sync` 3 项 + `test_tool_sync` 5 项）
- [x] 阶段7：同步 `compact.py` 21 个伞形工具的 action 参数文档
- [x] 审计指标：DEAD 44→0，MISSING 65→0，174:174 映射保持
- [x] 实机验证（Godot 4.7-beta3）：改动前复现 bug → 修复后回读属性确认真实写入

### 环境与配置
- [x] `pip install -e server` 可编辑安装
- [x] Cline MCP 配置文件已写入
- [x] `server/.gitignore` 已创建
- [x] `.clinerules/memory-bank.md` 翻译为中文
- [x] 记忆库初始化完成（6 个核心文件）

## 待办 / 进行中 🔧

### 端到端连通性（已验证 2026-07-30）
- [x] Godot 4.7-beta3 + 插件 v1.15.1 + Python server 全链路连通
- [x] `get_project_info` / `get_scene_tree` / `execute_editor_script` 正常返回
- [x] 实机验证 6 个修复项（含回读属性值确认真实生效）
- [x] 测试环境清理完毕，场景树还原

### 复测完成（2026-07-31，重启 Godot 后）
- [x] `search_in_files(file_type="*.gd")` → 3 条匹配（归一化生效）
- [x] `get_filesystem_tree(filter="gd")` → 裸扩展名展开为 `*.gd`
- [x] `set_editor_camera` → `rotation_degrees`/`fov` 生效；`look_at` 正确覆盖 `rotation`
- [x] `set_physics_layers` → `[1,3]`→5、掩码 12→层 3+4，`get_physics_layers` 独立回读一致
- [x] `setup_control` → `custom_minimum_size=(220,140)`、size_flags 3/4、
      `separation=17`（有 override）、4 个 `margin_*` 常量全部写入
- [x] `cross_scene_set_property` → dry-run 只扫 `path_filter` 目录；`force=true` 后
      离线场景落盘 + 活动场景实时写入，均已回读确认
- [x] 复测沙盒与上轮遗留文件全部删除，`_mcp_audit` 目录不再存在
- [ ] 仍未实测：`export_project` / `deploy_to_android`（测试项目无导出预设、无 ADB）
- [ ] 刻意不再触发：`bake_navigation_mesh`（上游冻结缺陷）

### 后续可选
- [ ] 实现 HTTP transport（`--http` 模式）
- [ ] 更新 `server/README.md`（仍写 172 工具、未提及 `--compact`）

## 已知问题 / 风险 ⚠️

1. ~~**未做过真实连通性测试**~~ → ~~仍有约 150 个工具未逐个实测~~ → **已完成 174 个
   工具全量逐一实机测试**（2026-07-30 首轮 + 2026-07-31 复测，详见
   `memory-bank/tool-live-test.md`）。
2. **参数腐化是静默的**：工具数量对齐 ≠ 参数对齐。上游改参数名时 Python 端不会报错，只会「调用成功但什么都没做」。**每次合并 upstream 必须跑 `python -m pytest server/tests/ -v`**。
3. **Windows 特定问题**：入口点脚本 `godot-mcp-pro.exe` 安装路径可能不在系统 PATH 中，需使用 `python -m` 方式启动。
4. **多 Cline 实例并发**：虽然端口重试已解决绑定冲突，但多个 MCP server 同时向 Godot 发命令时可能产生竞态（上游设计允许，但需注意）。
5. ⚠️ **upstream bug — `bake_navigation_mesh` 会冻结编辑器**：
   `navigation_commands.gd` 调用了 Godot 4.x 已废弃的
   `NavigationPolygon.make_polygons_from_outlines()`，在 4.7-beta3 上阻塞主线程直至
   WebSocket 断连，**必须重启编辑器**。Python 侧已把超时提到 120s 并在 docstring
   标注风险，但根因在 `addons/`（按约定不修）。
6. ⚠️ **测试方法论**：绝不能用 `batch_execute` 测试工具——它把原始命令透传给
   GDScript，绕过 Python 参数转换层，会得出假阴性结论。写入类工具必须回读校验。
7. **v1.15.1 引入的行为变化**（详见 `activeContext.md`）：
   - `get_scene_tree` 改为场景相对路径，但 `get_game_scene_tree` 仍是绝对路径 → 两者输出不一致
   - `PropertyParser._auto_parse` 会把 `res://`/`uid://` 字符串自动加载为 Resource，可能影响「本意存路径字符串」的 Variant 属性
   - `get_performance_monitors` 未运行游戏时直接报错（不再回退编辑器指标）
   - 上游 IPC 请求/响应使用固定文件名，`send_game_command` 与 `_send_game_command` 两份实现共用之，理论上并发会互踩（不修，避免分叉）

## 版本演进时间线
| 时间 | 事件 |
|------|------|
| 初始 | `cbb19f2` — 第一版 Python 迁移 |
| v1.13.1 适配 | `555865b` — 心跳 + 端口重试 |
| 上游合并 | `a47f61c` — Merge PR #1（v1.13.x） |
| 上游合并 | `542c8b4` — Merge PR #2（v1.14.0 安全性大修） |
| 参数适配 | `dc06930` — 配合 1.40 修改（v1.14.0 Python 适配） |
| 上游合并 | `350f649` — Merge PR #3（v1.14.1 assert_node_state 回归修复） |
| 全面审计 | `494ef09` — 参数审计修复 + 端口重试始终启用 |
| 上游合并 | `fa0ed7e` — Merge upstream/master（v1.15.0） |
| Python 适配 | `40d77dd` — 新增 editor selection 工具 + tilemap layer 参数 |
| 工具清理 | `fc970cd` — 删除 2 个幽灵工具，对齐 174:174 |
| 新增工具 | `b2a5ce5` — 新增 `batch_execute` 批量执行工具（175 tools） |
| 紧凑模式 | `4c00d89` — 添加 --compact 模式，175→22 工具合并 |
| 记忆库 | `ac3d8c0` — 紧凑模式实现记录 |
| 上游合并 | `ece45f9` — Merge upstream/master（v1.15.1，15 个 bug 修复） |
| Python 适配 | `e0f8287` — v1.15.1 Python 端跟进（connect_signal 参数 + 文档） |
| 参数对齐 1 | `8ebf4cc` — 11 个 P0 硬故障（调用必然报错） |
| 参数对齐 2 | `d3720f9` — 18 处 properties 包装失效（静默丢弃） |
| 参数对齐 3 | `c3212f7` — 14 处参数名/结构不一致 |
| 参数对齐 4 | `ba9deab` — 补齐 24 处未暴露的可选参数 |
| 参数对齐 5 | `c07aa04` — 清理 7 处无效参数（DEAD/MISSING 双清零） |
| 测试固化 | `058feb6` — 审计固化为 server/tests/（8 项） |
| 文档同步 | `843a2ab` — compact.py 21 个伞形工具 action 文档 |
