# 系统模式与架构

## 整体架构

```
AI 助手 (Cline/Claude)
    ↕ stdio (MCP 协议)
Python FastMCP Server (server/src/godot_mcp_pro/)
    ↕ WebSocket (JSON-RPC 2.0, 端口 6505-6514)
Godot 编辑器插件 (addons/godot_mcp/)
    ↕ EditorInterface / SceneTree API
Godot 引擎
```

## 通信协议

### MCP 层（AI ↔ Python Server）
- 传输方式：**stdio**（标准输入输出）
- 协议：MCP（Model Context Protocol）
- 框架：FastMCP（Python）

### Bridge 层（Python Server ↔ Godot Plugin）
- 传输方式：**WebSocket**
- 协议：**JSON-RPC 2.0**
- Python 端为 WS **Server**（监听），Godot 端为 WS **Client**（主动连接）
- 消息格式：`{"jsonrpc": "2.0", "method": "命令名", "params": {...}, "id": 123}`
- 响应格式：`{"jsonrpc": "2.0", "result": {...}, "id": 123}`

## 关键模式

### 1. 工具注册模式
- `server.py` 启动时调用 `_register_all_tools()`
- **完整模式**（默认）：24 个工具模块（`tools/*.py`）各自定义 `register(mcp, bridge)` → 共 187 个工具
  （186 GDScript 命令 + 1 纯 Python `batch_execute`）
- **紧凑模式**（`--compact`）：单一 `tools/compact.py` 注册 23 个伞工具（22 领域 + 1 batch_execute）
- 完整模式中每个工具函数内部调用 `bridge.call_godot("命令名", {...})`
- 紧凑模式中每个伞工具接受 `action:str` + `params:dict`，通过 ACTION_MAP 分发，再经
  `_call()`（参数转换 + 超时）调用 `bridge.call_godot()`
- ⚠️ **超时唯一来源 `godot_mcp_pro/timeouts.py` 的 `call_timeout(method, params)`**：完整模式工具、
  紧凑模式 `_call()`、两个 `batch_execute` 都用它。新增长耗时命令只改这一处，预算要高于 GDScript
  自己的截止时间。`server/tests/test_timeouts.py` 禁止工具里硬编码 `timeout=`，并逐个核对预算
- ⚠️ 紧凑模式**原样透传** `params`。完整模式工具若做了参数改名/结构转换（如 `edit_script` 的
  search→replacements、`set_physics_layers` 的 layer→collision_layer），紧凑模式必须在
  `PARAM_TRANSLATORS` 里做同样的转换，否则 docstring 写的参数名会被 GDScript 静默忽略。
  由 `test_compact_documented_params_are_read` 守卫
- ⚠️ 紧凑模式下 AI **只能靠 docstring 发现参数**（schema 里只有 `action`/`params`），
  所以完整模式的签名一改，`compact.py` 的 action 说明必须同步
- ⚠️ headless 工具（v1.16.0）：GDScript 读的参数 key 是 `args`（不是 `extra_args`）；
  Python 侧超时 = clamp(timeout_sec, 1, 900) + 30

### 2. 命令分发模式（GDScript 端）
- `command_router.gd` 维护命令分发表
- 27 个命令模块（`commands/*_commands.gd`）继承 `base_command.gd`（共注册 186 个命令；
  v1.16.0 新增 `headless_commands.gd` 的 3 个命令，v1.17.0 新增 9 个命令）
- `base_command.gd` 提供 UndoRedo、安全守卫（v1.14.0+）等公共方法
- 路由：method 名 → 对应的 command 类 → 执行并返回结果
- v1.16.0：handler 返回非 Dictionary 时返回错误而非挂起调用方；`optional_int`/`optional_float`
  防 raise（~160 处转换全部收紧）——**纯 GDScript 端加固，Python 无感**

### 3. 心跳保活模式
- **Python → Godot**：每 10s 发送 JSON-RPC `{"method": "ping"}`
- **Godot → Python**：每 5s 发送自己的 ping
- **超时判定**：30s 无活动 → 强制关闭连接
- **WebSocket 协议层**：`websockets` 库的 `ping_interval=10, ping_timeout=30`

### 4. 端口重试模式
- 默认端口：6505
- 重试范围：6505 → 6514（共 10 个端口）
- **始终启用重试**：先绑 `GODOT_MCP_PORT`，被占用再依次试范围内其余端口
- `GODOT_MCP_PORT` 超出 6505-6514 直接报错（Godot 插件只连这个范围，绑了也连不上）
- 多 Cline 实例：各自占用不同端口（6505、6506、...），Godot 自动连接所有可用 server
- 心跳任务按连接各自持有：旧连接被替换时只取消自己的 ping 任务，不会误杀新连接的

### 5. 安全守卫模式（v1.14.0+，GDScript 端）
- `guard_offline_scene_save(path)`：阻止写入已在编辑器中打开的场景
- `guard_text_resource_write(path, force)`：阻止写入已打开的脚本/着色器
- `execute_editor_script` 扫描危险 API 调用
- 错误码 `-32009`：资源冲突
- v1.16.0 新增：`guard_expected_extension(path, allowed, what)` 拒绝扩展名不匹配的写入；
  `paths_match()` 大小写不敏感比较（Windows/macOS 保护）；`create_scene`/`delete_scene`/
  `read_resource` 新增/收紧守卫

### 5b. 连接 token 认证模式（v1.16.0，opt-in）
- **Godot 端**：`godot_mcp_pro/require_connection_token` 项目设置（或 `GODOT_MCP_REQUIRE_TOKEN=1`）
  → token 写入 `user://mcp_auth_token`；连接建立后**立即发** `{"method":"auth_required"}`
- **Python 端**（`bridge.py`）：收到 `auth_required` → 读 `GODOT_MCP_TOKEN` 或 `GODOT_MCP_TOKEN_FILE`
  → 回 `{"method":"auth","params":{"token":...}}`；5s 内未认证 Godot 断开（关闭码 4001）
- **默认关闭**：不开启时 `_authed` 立即为 true，整个机制零成本
- 时序保证：Godot 在连接事件后立刻发 `auth_required`，Python 的
  `async for message in websocket` 循环能立即收到，无竞态

### 6. 参数传递模式（关键，易腐化）

GDScript 端从 `params: Dictionary` 里**按 key 名**读取参数，Python 端发什么 key
没有任何运行时校验。两边一旦不一致：
- 必填 key 名不对 → 调用**必然报错**
- 可选 key 名不对 → 调用**「成功」但什么都没做**（最危险，AI 会以为生效了）

**约定：`properties` 字典采用「传输层平铺」**

```python
# GDScript 读的是平铺 key（optional_float(params, "mass") 等），不是嵌套字典
return await bridge.call_godot("setup_physics_body", {
    **(properties or {}),   # 先展开
    "node_path": node_path, # 关键 key 放在后面，防止被 properties 覆盖
})
```

这样 AI 看到的工具签名保持 `properties: dict`（token 成本低、与紧凑模式契合），
而 GDScript 收到的是它期望的平铺结构。GDScript 以后新增 key，Python **无需改动**。

**例外**：`add_audio_bus_effect` 的 GDScript 读的是**嵌套**字典 `params["params"]`，
必须保持嵌套；`add_mesh_instance` 读嵌套的 `mesh_properties`。

**枚举值也要对齐**：GDScript 常用 `match` 匹配字面量，大小写敏感。
`setup_lighting` 只认 `"DirectionalLight3D"`，`add_mesh_instance` 只认 `"BoxMesh"`。
Python 端保留友好别名（`"directional"`/`"box"`）并在发送前用映射表转换。

### 7. 双向参数审计（`server/tests/`）

参数腐化是静默的，只能靠静态审计发现。两个测试文件守卫这个契约：

| 文件 | 检查项 |
|---|---|
| `test_param_sync.py` | ① 命令双向覆盖 ② **DEAD**：Python 发了但 GDScript 不读 ③ **MISSING**：GDScript 要读但 Python 不发 ④ 紧凑模式 docstring 参数必须被 GDScript 读取（或经 `PARAM_TRANSLATORS` 转换） |
| `test_tool_sync.py` | ① 完整/紧凑模式各自覆盖全部命令 ② 两模式暴露的命令集一致 ③ 完整模式工具数 = 命令数 + 纯 Python 工具 ④ 紧凑模式工具数守恒 |

实现要点：
- Python 侧用 `ast` 解析 `bridge.call_godot("cmd", {...})` 的字面量 key
- GDScript 侧用正则抓 `require_*` / `optional_*` / `params.has/get/[]`，并**递归跟进
  转发了 `params` 的辅助函数**（如 tilemap 的 `_get_single_layer`、v1.17 的
  `_build_blend_space(cond, params)` 和 `_edit_script_write.bind(path, params)`），否则会误报。
  两个脚本共用 `HELPER_CALL_PATTERNS`，改一处必须同步另一处
- 用计算出的 key 读参数（如 `"action_" + dir`）静态正则看不到，只能进 `ALLOWED_DEAD` 白名单并写明原因
- 提取命令表时必须要求值是 handler 引用（`"cmd": _cmd`），否则会把普通 Dictionary
  字面量误当成命令
- 条件构建 payload 的命令（`params: dict` 变量）无法静态判定 MISSING，已排除
- 预留 `ALLOWED_DEAD` / `ALLOWED_MISSING` 白名单，默认为空

**每次合并 upstream 前后都要跑**：`python -m pytest server/tests/ -v`

## 模块映射

### Python 工具模块 → GDScript 命令模块

| Python (tools/) | GDScript (commands/) |
|-----------------|---------------------|
| project.py | project_commands.gd |
| scene.py | scene_commands.gd |
| node.py | node_commands.gd |
| script.py | script_commands.gd |
| editor.py | editor_commands.gd |
| input_tools.py | input_commands.gd + input_map_commands.gd |
| runtime.py | runtime_commands.gd |
| animation.py | animation_commands.gd |
| audio.py | audio_commands.gd |
| batch.py | batch_commands.gd |
| export.py | export_commands.gd |
| navigation.py | navigation_commands.gd |
| particle.py | particle_commands.gd |
| physics.py | physics_commands.gd |
| profiling.py | profiling_commands.gd |
| resource.py | resource_commands.gd |
| scene_3d.py | scene_3d_commands.gd |
| shader.py | shader_commands.gd |
| test.py | test_commands.gd |
| theme.py | theme_commands.gd |
| tilemap.py | tilemap_commands.gd |
| analysis.py | analysis_commands.gd |
| android.py | android_commands.gd |
| headless.py | headless_commands.gd（v1.16.0 新增） |

### 辅助模块（GDScript）
- `websocket_server.gd`：WS 客户端管理、心跳、重连
- `plugin.gd`：EditorPlugin 生命周期
- `plugin.cfg`：插件元数据
- `mcp_game_inspector_service.gd`：运行时游戏检查（autoload）
- `mcp_input_service.gd`：输入模拟（autoload）
- `mcp_screenshot_service.gd`：截图采集（autoload）
- `ui/status_panel.gd`：编辑器底部面板 UI
- `utils/node_utils.gd`、`utils/property_parser.gd`：工具函数