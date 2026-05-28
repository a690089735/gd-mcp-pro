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
- 22 个工具模块（`tools/*.py`）各自定义 `register(mcp, bridge)` 函数
- 每个 `register()` 内部用 `@mcp.tool()` 装饰器注册若干工具函数
- 工具函数内部调用 `bridge.send_command("gd_命令名", {...})` 发送 JSON-RPC

### 2. 命令分发模式（GDScript 端）
- `command_router.gd` 维护命令分发表
- 26 个命令模块（`commands/*_commands.gd`）继承 `base_command.gd`
- `base_command.gd` 提供 UndoRedo、安全守卫（v1.14.0+）等公共方法
- 路由：method 名 → 对应的 command 类 → 执行并返回结果

### 3. 心跳保活模式
- **Python → Godot**：每 10s 发送 JSON-RPC `{"method": "ping"}`
- **Godot → Python**：每 5s 发送自己的 ping
- **超时判定**：30s 无活动 → 强制关闭连接
- **WebSocket 协议层**：`websockets` 库的 `ping_interval=10, ping_timeout=30`

### 4. 端口重试模式
- 默认端口：6505
- 重试范围：6505 → 6514（共 10 个端口）
- **始终启用重试**：无论 `GODOT_MCP_PORT` 是否设置，都从配置端口开始逐个尝试
- 多 Cline 实例：各自占用不同端口（6505、6506、...），Godot 自动连接所有可用 server

### 5. 安全守卫模式（v1.14.0+，GDScript 端）
- `guard_offline_scene_save(path)`：阻止写入已在编辑器中打开的场景
- `guard_text_resource_write(path, force)`：阻止写入已打开的脚本/着色器
- `execute_editor_script` 扫描危险 API 调用
- 错误码 `-32009`：资源冲突

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

### 辅助模块（GDScript）
- `websocket_server.gd`：WS 客户端管理、心跳、重连
- `plugin.gd`：EditorPlugin 生命周期
- `plugin.cfg`：插件元数据
- `mcp_game_inspector_service.gd`：运行时游戏检查（autoload）
- `mcp_input_service.gd`：输入模拟（autoload）
- `mcp_screenshot_service.gd`：截图采集（autoload）
- `ui/status_panel.gd`：编辑器底部面板 UI
- `utils/node_utils.gd`、`utils/property_parser.gd`：工具函数