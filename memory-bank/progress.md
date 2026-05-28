# 项目进度

## 已完成 ✅

### Python Server 核心实现
- [x] 从 Node.js/TypeScript 完整迁移为 Python FastMCP 实现
- [x] 22 个工具模块全部实现（`tools/*.py`）
- [x] WebSocket bridge 实现（`bridge.py`）
- [x] JSON-RPC 2.0 通信协议
- [x] FastMCP 工具注册框架（`server.py`）

### 工具对齐审计
- [x] Python 工具函数与 GDScript 命令一一对应（审计时为 173:173）
- [x] 修复 `android.py` 的 3 个命令名不匹配
- [x] 补齐 10 个缺失的工具暴露

### v1.13.x 适配
- [x] 心跳保活：Python 端每 10s 发送 JSON-RPC ping
- [x] 端口重试：bind 失败时自动尝试 6505-6514
- [x] 接收端 ping/pong 处理（Godot 发来的 ping 正确回复 pong）

### v1.14.0 上游合并
- [x] 通过 PR #2 合并上游 v1.14.0（GDScript 端安全性大修）
- [x] addon 的 UndoRedo、文件冲突守卫等功能已就位

### 环境与配置
- [x] `pip install -e server` 可编辑安装
- [x] Cline MCP 配置文件已写入
- [x] `server/.gitignore` 已创建
- [x] `.clinerules/memory-bank.md` 翻译为中文

## 待办 / 进行中 🔧

### ✅ v1.14.0 参数适配（已完成）
- [x] `create_script`/`edit_script` 添加 `force` 参数
- [x] `create_shader`/`edit_shader` 添加 `force` 参数
- [x] `cross_scene_set_property` 添加 `dry_run`/`force` 参数
- [x] `execute_editor_script` 添加 `allow_unsafe_editor_io` 参数
- [x] `edit_script` 重写参数构建：`search`/`replace` → `replacements` 数组，`line`/`insert` → `insert_at_line`/`text`
- [x] `edit_shader` 重写参数构建：`search`/`replace` → `replacements` 数组，只在有内容时发送 `content`
- [x] 新增 `edit_script` 的 `start_line`/`end_line` 行范围替换支持

### ⚠️ 端到端连通性（未验证）
- [ ] 启动 Godot 编辑器 + 启用插件
- [ ] 启动 Python server（`python -m godot_mcp_pro.server`）
- [ ] 通过 Cline 发送一个简单工具调用（如 `get_project_info`）验证全链路通
- [ ] 确认心跳正常工作（30s 内不断连）

### 工具数量同步
- [ ] 上游 v1.14.0 CHANGELOG 提到 172 工具，`llms.txt` 写 162，README 写 172——以实际 GDScript 命令注册数为准，需要重新统计确认

### 后续可选
- [ ] 实现 `--lite` 模式（仅注册核心工具子集）
- [ ] 实现 HTTP transport（`--http` 模式）
- [ ] 编写自动化测试

## 已知问题 / 风险 ⚠️

1. **工具参数签名可能不完整**：v1.14.0 新增了多个可选参数（`force`、`dry_run`、`allow_unsafe_editor_io`），如果 Python 工具函数使用显式参数而非 kwargs 透传，这些参数不会被传递到 GDScript 端。
2. **工具数量可能不一致**：上游持续增加工具，每次合并后需要重新审计 Python 端是否跟上。
3. **未做过真实连通性测试**：所有代码修改都通过语法检查和静态审计验证，但未在实际 Godot 实例上运行过。
4. **Windows 特定问题**：入口点脚本 `godot-mcp-pro.exe` 安装路径可能不在系统 PATH 中，需使用 `python -m` 方式启动。

## 版本演进时间线
| 时间 | 事件 |
|------|------|
| 初始 | `cbb19f2` — 第一版 Python 迁移 |
| v1.13.1 适配 | `555865b` — 心跳 + 端口重试 |
| 上游合并 | `a47f61c` — Merge PR #1（v1.13.x） |
| 上游合并 | `542c8b4` — Merge PR #2（v1.14.0 安全性大修） |