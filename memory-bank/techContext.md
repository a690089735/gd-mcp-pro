# 技术上下文

## 技术栈

### Python Server 端
- **语言**：Python 3.10+
- **MCP 框架**：FastMCP ≥ 2.0.0
- **WebSocket**：websockets ≥ 12.0
- **构建系统**：Hatchling
- **入口点**：`godot_mcp_pro.server:main`

### Godot 插件端
- **引擎**：Godot 4.x（4.3+ 兼容）
- **语言**：GDScript
- **通信**：WebSocket 客户端（内建 `WebSocketPeer`）
- **运行时服务**：3 个 autoload（game_inspector、input_service、screenshot_service）

### 协议
- **AI ↔ Server**：MCP over stdio
- **Server ↔ Godot**：JSON-RPC 2.0 over WebSocket

## 开发环境配置

### 安装
```bash
# 进入 server 目录安装为 editable 包
cd <项目根目录>/server
pip install -e .
```

### 运行
```bash
# 直接运行模块
python -m godot_mcp_pro.server

# 或使用入口点脚本（需确保 Scripts 目录在 PATH 中）
godot-mcp-pro
```

### 环境变量
| 变量 | 默认值 | 说明 |
|------|--------|------|
| `GODOT_MCP_PORT` | 6505 | WebSocket 监听端口。未设置时启用端口重试（6505-6514）。|

### Cline MCP 配置
配置文件位于：`<APPDATA>/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "godot-mcp-pro": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "python",
      "args": ["-m", "godot_mcp_pro.server"],
      "env": { "GODOT_MCP_PORT": "6505" }
    }
  }
}
```

### Godot 端配置
1. 将 `addons/godot_mcp/` 目录放入 Godot 项目
2. 在 Godot 编辑器中：Project → Project Settings → Plugins → 启用 "Godot MCP"
3. 编辑器底部出现 "MCP Pro" 面板表示插件已激活

## 技术约束
- Python server 通过 **stdio** 与 MCP 客户端通信，不能在同一进程中使用 stdin/stdout 做其他用途
- WebSocket 连接要求 Godot 编辑器正在运行且插件已启用
- 运行时工具（`simulate_*`、`get_game_*`）需要游戏正在运行（通过 `play_scene` 启动）
- 截图功能返回 base64 图片或保存到磁盘路径
- v1.14.0+ 的安全守卫会拒绝写入已打开的文件（错误码 -32009），需要 `force=true` 覆盖

## 依赖项

### Python（`server/pyproject.toml`）
```toml
[project]
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=2.0.0",
    "websockets>=12.0",
]
```

### Godot
- 无外部依赖，纯 GDScript 实现
- 使用 Godot 内建的 `WebSocketPeer`、`EditorInterface`、`EditorUndoRedoManager` 等 API

## 目录结构
```
godot-mcp-pro/
├── addons/godot_mcp/          # Godot 编辑器插件（从上游同步）
│   ├── commands/              # 26 个命令模块
│   ├── ui/                    # 编辑器底部面板
│   ├── utils/                 # 工具函数
│   ├── plugin.gd             # 插件入口
│   ├── websocket_server.gd   # WS 客户端 + 心跳
│   └── plugin.cfg            # 插件元数据
├── server/                    # Python MCP Server（本 fork 独有）
│   ├── src/godot_mcp_pro/
│   │   ├── server.py         # FastMCP 入口、工具注册
│   │   ├── bridge.py         # WebSocket 桥接、心跳、端口重试
│   │   └── tools/            # 22 个工具模块
│   ├── pyproject.toml        # 构建配置
│   └── README.md             # Server 说明
├── docs/                      # 多语言 README
├── memory-bank/               # Cline 记忆库
└── .clinerules/               # Cline 规则文件