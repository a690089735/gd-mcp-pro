# 当前活跃上下文

## 当前工作焦点
完成 v1.14.1 合并适配，并修复全面审计中发现的参数不匹配问题。

## 仓库当前状态
- **最新 commit**：`350f649` — Merge pull request #3 from youichi-uda/master（合并上游 v1.14.1）
- **上游版本**：v1.14.1（`assert_node_state` 游戏端处理器回归修复）
- **Python server 版本**：1.0.0（`pyproject.toml`）

## 近期完成的工作

### 第五阶段：v1.14.0 参数适配
- `edit_script` 重写参数构建（`replacements` 数组、`insert_at_line`/`text`、`start_line`/`end_line`）
- `create_script`/`edit_script` 添加 `force` 参数
- `create_shader`/`edit_shader` 添加 `force` 参数 + `replacements` 数组
- `cross_scene_set_property` 添加 `dry_run`/`force`
- `execute_editor_script` 添加 `allow_unsafe_editor_io`

### 第六阶段：v1.14.1 合并 + 全面参数审计
- 合并 PR #3（v1.14.1：恢复 `assert_node_state` 游戏端处理器）
- **全面交叉审计**：所有 22 个 Python 工具文件 vs 26 个 GDScript 命令文件
- 发现并修复 5 处参数不匹配：
  1. `assert_node_state`（test.py）：`assertions: dict` → `property` + `expected` + `operator`
  2. `connect_signal`（node.py）：`node_path` → `source_path`，`method` → `method_name`
  3. `disconnect_signal`（node.py）：同上
  4. `run_test_scenario`（test.py）：补充 `scene_path` 可选参数
  5. `assert_screen_text`（test.py）：补充 `partial` + `case_sensitive` 可选参数

### 第七阶段：端口绑定修复
- 诊断间歇性 `OSError 10048`（端口已占用）
- 根因：多个 Cline 窗口各启动一个 Python MCP server 实例，竞争同一端口
- 修复：`server.py` 中始终启用 `port_retry=True`（不再受 `GODOT_MCP_PORT` 环境变量影响）

## 下一步计划
1. **端到端连通性测试**：启动 Godot + Python server，验证 Cline 能否成功调用工具
2. **跟进上游新版本**：监控 upstream 是否有新 commit 需要合并
3. 可选：实现 `--lite` 模式过滤

## 重要决策记录
- Python server 作为 WS **Server**（监听端），Godot 作为 WS **Client**（连接端）
- 不实现上游的 `--lite`/`--minimal`/`--3d` 模式过滤——Python 版暴露全部工具
- 不实现上游的 CLI 工具和 HTTP transport
- ~~环境变量 `GODOT_MCP_PORT` 显式设置时跳过端口重试~~ → **已改为始终启用端口重试**，`GODOT_MCP_PORT` 仅决定起始端口的偏好

## 重要模式与偏好
- 路径信息在文档中**一律脱敏**（使用 `<APPDATA>`、`<项目根目录>` 等占位符）
- 未经验证的事项显式标注 `⚠️`
- 中文作为项目文档和 Cline 交互的主要语言