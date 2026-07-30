# 当前活跃上下文

## 当前工作焦点
已同步上游 v1.15.1（15 个 bug 修复），Python 端已跟进适配。稳定维护阶段。

## 仓库当前状态
- **最新 commit**：`ece45f9` — Merge upstream/master (v1.15.1) + Python 端适配
- **上游版本**：v1.15.1（外部完整工具集审计的 15 个修复）
- **Python server 版本**：1.0.0（`pyproject.toml`）
- **工具总数**：
  - 完整模式（默认）：175 工具（174 GDScript 命令 + 1 纯 Python `batch_execute`）
  - 紧凑模式（--compact）：22 工具（21 领域工具 + 1 `batch_execute`）

## 近期完成的工作

### 第十阶段：同步上游 v1.15.1（本次会话）
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
1. **端到端连通性测试**：启动 Godot + Python server，验证 Cline 能否成功调用工具（尤其是新走 IPC 的 `get_performance_monitors`）
2. **跟进上游新版本**：监控 upstream 是否有新 commit 需要合并
3. 可选：编写自动化测试；可选：把映射校验脚本固化为 `server/tests/`

## 重要决策记录
- Python server 作为 WS **Server**（监听端），Godot 作为 WS **Client**（连接端）
- `--compact` 模式通过命令行参数启用，不使用环境变量
- 紧凑模式纯 Python 层面实现（`compact.py` 是分发器），零 GDScript 改动
- 紧凑模式使用 `action:str` + `params:dict` 统一签名，docstring 列出所有可用 action 及参数类型
- 工具总数 175（完整模式）/ 22（紧凑模式），与 upstream README 一致
- `GODOT_MCP_PORT` 仅决定起始端口偏好，始终启用端口重试（6505-6514）
- **不修改 `addons/` 下任何文件**，保持与 upstream 完全一致以确保后续合并永远零冲突；上游的技术债只记录不修

## 重要模式与偏好
- 路径信息在文档中**一律脱敏**（使用 `<APPDATA>`、`<项目根目录>` 等占位符）
- 未经验证的事项显式标注 `⚠️`
- 中文作为项目文档和 Cline 交互的主要语言