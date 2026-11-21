# Fork 对 `addons/` 的改动（合并上游时必读）

本 fork 原则上不改 `addons/`（上游原样同步）。**唯一例外是连接文件模式**（2026-11-21），因为端口问题
只能两端一起改。本文件列出全部改动，合并上游时照着核对；改动以外的 `addons/` 文件仍以上游为准。

## 为什么改

上游方案：MCP 服务器监听固定端口 6505-6514，每个编辑器连这 10 个端口上的所有服务器。两个问题：

1. **端口被系统保留就整体失效**：Windows 的动态端口区间从 1024 开始时，Hyper-V / WinNAT 会保留一批端口
   （`netsh interface ipv4 show excludedportrange protocol=tcp` 能看），落在 6505-6514 上时绑定报
   `WinError 10013`。哪些端口被保留每台机器不同、重启还会变，不可能要求每台机器改系统设置。
2. **多开会串**：每个编辑器都连所有服务器，服务器同时只留一个连接、新的踢掉旧的，开两个工程时
   两个编辑器反复互踢，命令可能落到另一个工程。

## 方案（连接文件模式）

- **编辑器监听**：`mcp_listener.gd` 用端口 0 让系统分配端口（系统给的一定能绑），把端口、一次性令牌、
  进程号、工程路径写进 `res://.godot/mcp_connection.json`（`.godot/` 本来就不进版本库）。
  正常退出时删掉（仍是自己写的才删：同一工程的另一个编辑器可能已经接管）。
- **服务器连接**：服务器找到自己的工程（`GODOT_MCP_PROJECT` → 工作目录及其上级 → MCP 客户端的
  roots），读文件，作为客户端连上去，第一条消息发 `auth`（带令牌），编辑器回工程路径，服务器核对。
- **认证通过后**连接交给 `websocket_server.gd`，从此和上游的连接走同一条路（命令分发、ping/pong、
  响应、`send_message` 广播、`get_client_count`）。连接的 key 从 70000 起（`KEY_BASE`），不会和
  6505-6514 撞；上游 `_process` 只遍历 6505-6514，不碰这些连接，轮询由 `mcp_listener.gd` 自己做。
- **固定端口照旧**：编辑器仍连 6505-6514（上游行为不变），没升级的服务器、别的客户端照常能用。

## 改动清单

| 文件 | 改动 | 合并上游时 |
|---|---|---|
| `mcp_listener.gd` | **新文件**（fork 独有） | 上游不会有，保留 |
| `websocket_server.gd` | ① 变量区加 `var _listener: Node`；② `start_server()` 开头调 `_start_listener()`；③ `stop_server()` 开头调 `_stop_listener()`；④ 文件末尾 `# --- FORK: connection-file listener hooks` 整块（`_start_listener`、`_stop_listener`、`get_listener_port`、`is_listener_key`、`register_listener_peer`、`unregister_listener_peer`、`dispatch_listener_message`） | ①②③ 是单行，冲突时手工补回；④ 在文件末尾，一般不冲突。**核对上游是否改了 `_dispatch_message(text, source_port)`、`_send_to_port`、各个 per-port 字典的名字**，改了要同步 `register_listener_peer` / `unregister_listener_peer` |
| `ui/status_panel.gd` | 变量 `_listener_label`；`_build_clients_tab()` 末尾加一行标签；`_update_clients_tab()` 开头更新这行（用 `has_method` 判断，老服务器节点也不报错） | 冲突时手工补回 |
| `plugin.gd` | 启动日志里加 `project port %d` | 冲突时以上游为准再补回 |

所有改动处都有 `FORK` 注释，`git grep -n FORK addons/` 能列全。

## 合并上游后的核对步骤

1. `git grep -n FORK addons/` 确认上面 4 个文件的改动都在。
2. 解析检查：把 `addons/godot_mcp/` 复制进测试工程，
   `godot --headless --path <测试工程> --editor --quit-after 60`，输出里要有
   `[MCP] Listening on 127.0.0.1:<端口> for this project's MCP server`，且没有脚本错误。
3. `python server/tests/test_connection_file.py`（不需要 Godot）。
4. 真编辑器端到端（需要 Godot，步骤见 `systemPatterns.md`「连接文件模式」）。

## 同步到使用方工程

使用方工程（例如用团队引擎开发的 Godot 游戏）里的 `addons/godot_mcp/` 要整体换成本 fork 的版本，
**不能只拷 `mcp_listener.gd`**（`websocket_server.gd` 的钩子也要）。旧插件 + 新服务器也能用（退回
固定端口），但端口被保留时连不上。
