# 当前活跃上下文

## 当前工作焦点
完成 v1.15.0 合并适配，工具数量精确对齐 174:174。

## 仓库当前状态
- **最新 commit**：`fc970cd` — 删除 2 个幽灵工具，对齐 174:174
- **上游版本**：v1.15.0（editor selection tools + legacy TileMap support）
- **Python server 版本**：1.0.0（`pyproject.toml`）
- **工具总数**：Python 174 : GDScript 174（精确匹配）

## 近期完成的工作

### 第八阶段：v1.15.0 合并 + Python 适配（本次会话）
- 合并 upstream v1.15.0（6 个提交），解决 README.md 冲突（工具数 173→175）
- **node.py** 新增 3 个编辑器选择工具：
  - `get_editor_selection(top_only)` — 获取当前选中的场景节点
  - `select_nodes(node_path/node_paths, mode, inspect, focus, ...)` — 选中/聚焦/检查节点
  - `clear_editor_selection()` — 清除编辑器选择
- **tilemap.py** 给 4 个工具添加 `layer` 参数（兼容已弃用的 TileMap 多层节点）：
  - `tilemap_set_cell` / `tilemap_fill_rect` / `tilemap_get_cell` / `tilemap_get_used_cells` → `layer: int = 0`
  - `tilemap_clear` → `layer: int = -1`（-1 表示清除所有层）
- **physics.py** 删除 2 个无 GDScript 后端的幽灵工具：
  - `collision_layer_info` / `collision_mask_info`（功能已包含在 `get_physics_layers` 返回数据中）

### 不需要 Python 配合的 GDScript 内部改动
- `base_command.gd`：新增共享方法 `build_timeout_error()`、`try_debugger_continue()`、`is_debugger_paused()` 等
- `runtime_commands.gd` / `test_commands.gd`：超时错误改用 `build_timeout_error()`
- `plugin.gd`：debugger Continue 按钮改为图标匹配（locale-independent，修复 #34）

## 下一步计划
1. **端到端连通性测试**：启动 Godot + Python server，验证 Cline 能否成功调用工具
2. **跟进上游新版本**：监控 upstream 是否有新 commit 需要合并
3. 可选：实现 `--lite` 模式过滤

## 重要决策记录
- Python server 作为 WS **Server**（监听端），Godot 作为 WS **Client**（连接端）
- 不实现上游的 `--lite`/`--minimal`/`--3d` 模式过滤——Python 版暴露全部工具
- 不实现上游的 CLI 工具和 HTTP transport
- `GODOT_MCP_PORT` 仅决定起始端口的偏好，始终启用端口重试（6505-6514）
- upstream README 写 175 是因为他们的 Node.js 服务端计数方式不同，我们以 Python↔GDScript 1:1 匹配为准（174:174）

## 重要模式与偏好
- 路径信息在文档中**一律脱敏**（使用 `<APPDATA>`、`<项目根目录>` 等占位符）
- 未经验证的事项显式标注 `⚠️`
- 中文作为项目文档和 Cline 交互的主要语言