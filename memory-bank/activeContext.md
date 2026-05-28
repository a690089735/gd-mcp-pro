# 当前活跃上下文

## 当前工作焦点
适配 v1.14.0 上游合并后 Python server 的参数兼容性问题。

## 仓库当前状态
- **最新 commit**：`542c8b4` — Merge pull request #2 from youichi-uda/master（合并上游 v1.14.0）
- **上游版本**：v1.14.0（文件冲突安全性大修）
- **Python server 版本**：1.0.0（`pyproject.toml`）

## 近期完成的工作

### 第一阶段：Python 迁移基础修复
- 修复 `android.py` 的 3 个 bridge 命令名不匹配（`android_list_devices` → `list_android_devices` 等）
- 补齐 Python 端缺失的 10 个工具暴露（`set_auto_dismiss`、`watch_signals`、`get_scene_exports` 等）
- 最终确认 Python 工具数与 GDScript 命令数**一一对应**

### 第二阶段：适配上游 v1.13.x
- 实现 WebSocket 端口重试循环（6505-6514），对应 v1.13.2 的端口冲突修复
- 实现 JSON-RPC 心跳 ping（10s 间隔），对应 v1.13.1 的静默断连修复
- 添加 `bridge.py` 中的 `_ping_loop`、`_start_with_retry` 等方法

### 第三阶段：环境配置
- 将 Python server 通过 `pip install -e` 安装为可编辑包
- 配置 Cline MCP settings（stdio 模式，`python -m godot_mcp_pro.server`）
- 创建 `server/.gitignore`

### 第四阶段：合并上游 v1.14.0
- 通过 PR #2 合并 youichi-uda/master（v1.14.0 安全性大修）
- 包含 UndoRedo 全面接入、文件冲突守卫、`force`/`dry_run` 参数等

## 下一步计划
1. **端到端连通性测试**：启动 Godot + Python server，验证 Cline 能否成功调用工具
2. **跟进上游新版本**：监控 upstream 是否有新 commit 需要合并
3. 可选：实现 `--lite` 模式过滤

## 重要决策记录
- Python server 作为 WS **Server**（监听端），Godot 作为 WS **Client**（连接端）——与上游 Node.js 版本的角色一致
- 不实现上游的 `--lite`/`--minimal`/`--3d` 模式过滤——Python 版暴露全部工具
- 不实现上游的 CLI 工具和 HTTP transport
- 环境变量 `GODOT_MCP_PORT` 显式设置时跳过端口重试

## 重要模式与偏好
- 路径信息在文档中**一律脱敏**（使用 `<APPDATA>`、`<项目根目录>` 等占位符）
- 未经验证的事项显式标注 `⚠️`
- 中文作为项目文档和 Cline 交互的主要语言