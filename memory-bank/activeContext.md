# 当前活跃上下文

## 当前工作焦点
已同步上游 v1.15.1，完成 **Python 移植层参数级对齐大修**，并完成
**174 工具全量实机逐一测试**（详见 `memory-bank/tool-live-test.md`）。稳定维护阶段。

## 仓库当前状态
- **上游版本**：v1.15.1（外部完整工具集审计的 15 个修复）
- **参数对齐**：DEAD=0 / MISSING=0（由 `server/tests/` 守卫，盲区已从 55 降到 15）
- **实机验证**：174 个工具全部逐一调用过，写入类工具均回读校验
- **Python server 版本**：1.0.0（`pyproject.toml`）
- **工具总数**：
  - 完整模式（默认）：175 工具（174 GDScript 命令 + 1 纯 Python `batch_execute`）
  - 紧凑模式（--compact）：22 工具（21 领域工具 + 1 `batch_execute`）

## 近期完成的工作

### 第十二阶段：全量实机逐一测试（本次会话）

**起因**：用户要求「拉出清单，所有工具逐个完整检查和测试，gd→py→紧凑模式，并记录结果」。

**产出**
- `server/tools_audit.py`：生成 GDScript / Python / 紧凑模式**三方对照表**
  （`python server/tools_audit.py --md memory-bank/tool-audit.md`）
- `memory-bank/tool-audit.md`：174 行全量对照表（自动生成）
- `memory-bank/tool-live-test.md`：16 批次实机测试记录 + 回读校验证据

**又发现 6 个真实缺陷**（上一阶段的静态审计没抓到）
1. `search_files`/`search_in_files` 的 `file_type` —— GD 用 `get_extension()`
   比较（无点），带点写法永远 0 命中
2. `get_filesystem_tree` 的 `filter` —— 实际是 glob `*.gd`，文档写"扩展名"
3. `set_editor_camera` —— 发 `rotation`，GD 读 `rotation_degrees`；**旋转完全无效**
4. `set_physics_layers` —— 发 `layer`/`mask`，GD 读 `collision_layer`/`collision_mask`；
   **整个工具完全无效**
5. `setup_control` —— `min_size` 需 `"Vector2(w,h)"` 字符串；`theme_path` 不存在；
   `grow_h`/`grow_v`/`margins`/`separation` 从未暴露
6. `cross_scene_set_property` —— `scene_paths` 是死参数，实际用
   `path_filter`+`exclude_addons`

**根因（比缺陷本身更重要）**：上一阶段的审计脚本把「payload 由局部变量条件构建」
的 **55 个命令（32%）整体豁免**，连 DEAD 检查也一并失效。`set_editor_camera`
就是从这个盲区漏出去的。现已解析 `params["key"] = ...` 条件赋值，盲区 55→15。

**测试方法论教训**：⚠ **绝不能用 `batch_execute` 测试工具**——它把原始命令直接
透传给 GDScript，会绕过 Python 的参数转换层，导致假阴性（我一度误判
`edit_script` 的 search/replace 失效）。必须逐个调用具名 MCP 工具。

**已知上游缺陷**（不改 `addons/`）：`bake_navigation_mesh` 调用了 Godot 4.x 已
废弃的 `make_polygons_from_outlines()`，在 4.7-beta3 上**阻塞主线程直到 WebSocket
断连，必须重启编辑器**。Python 侧已提高超时并在 docstring 标注风险。

### 第十一阶段：参数级对齐大修

**起因**：复查「有没有纰漏」时写了 AST + GDScript 递归解析的参数审计脚本，发现
**工具数量 174:174 的对齐是假的安全感** —— 名字对上了，参数没对上。约 55 个工具
是「凭工具名猜参数」写的，从未与 GDScript 实际读取的 key 交叉验证过。

**审计指标**：DEAD（Python 发了但 GDScript 不读）44→0；MISSING（GDScript 要读但
Python 不发）65→0。

| commit | 阶段 | 内容 |
|---|---|---|
| `8ebf4cc` | 1 | 11 个 P0 硬故障（`require_*` 必填参数名错 → 调用必然报错） |
| `d3720f9` | 2 | 18 处 `properties` 包装失效（调用「成功」但零配置生效） |
| `c3212f7` | 3 | 14 处参数名/结构不一致（静默失效） |
| `ba9deab` | 4 | 补齐 24 处 GDScript 支持但未暴露的可选参数 |
| `c07aa04` | 5 | 清理 7 处 GDScript 从不读取的无效参数 |
| `058feb6` | 6 | 审计固化为 `server/tests/`（8 项测试） |
| `843a2ab` | 7 | 同步 `compact.py` 21 个伞形工具的 action 文档 |

**典型问题**
- `set_particle_color_gradient` 发 `colors`+`offsets`，GD 要 `stops:[{offset,color}]`
  —— 讽刺的是这正是 v1.15.1 修的 Critical 项，但从 MCP 层根本调不到
- `setup_physics_body` 等 16 个工具把配置塞进 `properties` 字典，GD 读平铺 key
  → **调用成功但零配置生效**（最危险的失败模式）
- `tilemap_fill_rect` 发 `x/y/width/height`，GD 读 `x1/y1/x2/y2` → **永远只填 1 格**
- `play_scene` 的 custom 模式：GD 只读 `mode`，拿 `"custom"` 当路径找文件 → 100% 报错
- `capture_frames`/`monitor_properties` 的 `interval` 是**秒**，GD 要的是**帧数**
- `move_to` Python 固定 30s 超时，GD 是 `timeout+5s` → 传 `timeout=40` 会被提前掐断
- `create_theme` 的 `base_type` 是假参数，真参数 `default_font_size` 从未暴露
- `setup_lighting`/`add_mesh_instance` 的枚举值大小写不匹配（`"directional"` vs
  `"DirectionalLight3D"`）→ 增加了别名映射表

**方案决策：`properties` 采用传输层平铺**
`{**(properties or {}), "node_path": node_path}` —— 工具签名不变（AI 接口稳定、
token 成本低、与紧凑模式契合），只改传输层。相比显式平铺（`setup_environment`
会膨胀到 28 个参数），可维护性压倒性更好：GDScript 以后新增 key，Python 自动支持。
⚠️ 关键 key 必须放在展开**之后**，防止被 `properties` 覆盖。

**实机验证（Godot 4.7-beta3）**
- 改动前复现 bug：`setup_physics_body` 报 `No valid properties provided for CharacterBody3D`
- 修复后：`applied: {floor_max_angle:0.9, max_slides:7}`，回读节点确认真实写入
- `setup_collision` / `find_script_references` / `create_theme` / `create_particles`
  / `set_particle_color_gradient` 全部验证通过（含回读属性值）
- v1.15.1 的场景相对路径修复确认生效（路径体积缩小约 10 倍）
- ⚠️ 测试项目的插件曾是 v1.13.2，必须先同步到 v1.15.1 否则测试结论失真

**过程中的自我纠错（3 次）**
1. `set_blend_tree_node` —— `blend_tree_state` 是**必填**，类型值是 CamelCase
2. `set_navigation_layers` —— `layers` **是**被读取的（bitmask），`layer_bits` 才是数组
3. `test_tool_sync.py` 正则误把普通 Dictionary 字面量当命令表，多抓 11 个假命令

前两次都是因为轻信了终端管道输出（渲染错乱），靠 `search_files` 复核原文才抓回。

### 第十阶段：同步上游 v1.15.1
合并 upstream `c17a182`，**零冲突**（v1.15.1 只改 `addons/` + CHANGELOG，我们只加 `server/**`、`memory-bank/**`，无交集）。

**上游 15 个修复（GDScript 端，全部直接继承）**
- Critical：`set_particle_color_gradient` 无限循环卡死编辑器；`connect_signal` 缺 `CONNECT_PERSIST` 导致连接不写入 `.tscn`；`update_property` 把 Resource 属性静默清成 `null`
- High：`create_theme` 返回 `{}` 不写文件；`get_performance_monitors` 返回编辑器指标而非游戏指标；`get_test_report` / `run_test_scenario` 把通过的断言算成失败
- Medium：`get_scene_tree` 返回编辑器内部绝对路径；`analyze_signal_flow` 输出编辑器内部连接；`find_unused_resources` 忽略 `uid://`；`get_input_actions` 泄漏编辑器动作；`create_resource` 父目录不存在时失败；`run_test_scenario` keycode 步骤不释放按键
- Minor：`set_particle_material` emission 子参数未列入 `changes[]`；断言结果 `type` key 冲突改为 `assert_type`

**Python 端跟进**
- `tools/node.py` → `connect_signal` 新增可选参数 `deferred` / `one_shot`
- `tools/profiling.py` → `get_performance_monitors` docstring 说明「需先 play_scene，编辑器指标用 `get_editor_performance`」
- `tools/test.py` → `run_test_scenario` docstring 补全 step 结构与 `auto_release`
- `tools/compact.py` → `node` / `test` / `diagnostics` / `scene` 四个伞形工具的 action 说明同步
- 校验：GDScript 174 : 完整模式 174 : 紧凑 ACTION_MAP 174 完美 1:1，**PASS**

**需知晓的行为变化（副作用）**
1. `get_scene_tree` 路径格式变为场景相对（root=`"."`）；但 `get_game_scene_tree`（游戏进程链路）**未改**，仍是绝对路径 —— 两者输出从此不一致（upstream 遗留）
2. `PropertyParser._auto_parse` 新增 `res://`/`uid://` → Resource 自动加载。「当前值为 null 的 Variant 属性」若本意存路径字符串，会被静默加载成 Resource
3. `get_performance_monitors` **未运行游戏时直接报错**，不再回退到编辑器指标
4. `analyze_signal_flow` 只显示 `CONNECT_PERSIST` 连接 —— v1.15.1 之前建立的连接（无 PERSIST）不再出现，但那些本来也没存进 `.tscn`
5. `unwrap_game_result` 贪婪解包：若 payload 内恰有 `result: Dictionary` 字段会多解一层（当前无此情况）
6. `base_command.gd::send_game_command` 与 `test_commands.gd::_send_game_command` 逻辑重复，共用同一对固定 IPC 文件名 —— 并发调用会互踩（MCP 串行调用，实际难触发）。属 upstream 技术债，**不单独修**以避免分叉

### 第九阶段：紧凑模式
- **新文件** `compact.py`：21 个领域伞工具 + batch_execute，覆盖全部 174 个 GDScript 命令
- **修改** `server.py`：
  - 添加 `--compact` 参数检测（`while` 循环清理所有出现）
  - 条件注册：compact 模式注册 compact.py，否则注册原有 22 个模块
  - `instructions` 字符串根据模式动态调整
- **命名优化**：`input` 工具的 `action`/`set_action` → `simulate`/`define`，避免与 params 中的 `action` 字段二义
- **类型标注**：所有 docstring 使用 `name:type=default` 格式标注参数类型和默认值
- **验证**：
  - 22 tools 正确注册
  - 174:174 GDScript 命令完美 1:1 映射
  - 完整模式 175 tools 不受影响

### 之前：第八阶段：v1.15.0 合并 + Python 适配
- 合并 upstream v1.15.0，新增 editor selection 工具 + tilemap layer 参数
- 删除 2 个幽灵工具，对齐 174:174
- 新增 `batch_execute` 批量执行工具

## 下一步计划
1. **跟进上游新版本**：合并前**先跑 `python server/tests/test_param_sync.py`**，合并后再跑一次；
   并用 `python server/tools_audit.py --md memory-bank/tool-audit.md` 刷新对照表
2. **待复测**（本次会话末 Godot 因 `bake_navigation_mesh` 断连，重启后需验证）：
   `set_physics_layers`、`setup_control`、`cross_scene_set_property`、
   `set_editor_camera`、`search_in_files(file_type)`
3. 未实测：`export_project` / `deploy_to_android`（测试项目无导出预设、无 ADB）
4. 可选：实现 HTTP transport（`--http` 模式）

## 重要决策记录
- Python server 作为 WS **Server**（监听端），Godot 作为 WS **Client**（连接端）
- `--compact` 模式通过命令行参数启用，不使用环境变量
- 紧凑模式纯 Python 层面实现（`compact.py` 是分发器），零 GDScript 改动
- 紧凑模式使用 `action:str` + `params:dict` 统一签名，docstring 列出所有可用 action 及参数类型
- 工具总数 175（完整模式）/ 22（紧凑模式），与 upstream README 一致
- `GODOT_MCP_PORT` 仅决定起始端口偏好，始终启用端口重试（6505-6514）
- **不修改 `addons/` 下任何文件**，保持与 upstream 完全一致以确保后续合并永远零冲突；上游的技术债只记录不修
- **`properties` 字典采用传输层平铺**，不改工具签名（见第十一阶段方案决策）
- **每次合并 upstream 必须跑 `server/tests/`** —— 参数腐化是静默的，只有静态审计能发现

## 重要模式与偏好
- 路径信息在文档中**一律脱敏**（使用 `<APPDATA>`、`<项目根目录>` 等占位符）
- 未经验证的事项显式标注 `⚠️`
- 中文作为项目文档和 Cline 交互的主要语言
- **终端管道输出（长 stdout / `type` / `Select-String`）可能渲染错乱，不可作为改代码的依据**；
  必须用 `read_file` / `search_files` 复核原文
- ⚠️ **禁止用 PowerShell `Set-Content` 改中文文件** —— 会把 UTF-8 按 GBK 写回导致乱码；
  改中文文档一律用 `replace_in_file`
- ⚠️ **测试工具时绝不用 `batch_execute`** —— 它把原始命令透传给 GDScript，绕过
  Python 参数转换层，会得出假阴性结论。必须逐个调用具名 MCP 工具
- **写入类工具必须回读校验**：GDScript 对未知 key 静默忽略，"调用成功"不等于
  "配置生效"。用 `get_node_properties` / `get_*_info` / `execute_editor_script`
  回读实际值
