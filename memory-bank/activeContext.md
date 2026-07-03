# 当前活跃上下文

## 当前工作焦点
紧凑模式(--compact)已实现并推送，进入稳定维护阶段。

## 仓库当前状态
- **最新 commit**：`4c00d89` — 添加紧凑模式(--compact)，175工具合并为22个领域工具
- **上游版本**：v1.15.0（editor selection tools + legacy TileMap support）
- **Python server 版本**：1.0.0（`pyproject.toml`）
- **工具总数**：
  - 完整模式（默认）：175 工具（174 GDScript 命令 + 1 纯 Python `batch_execute`）
  - 紧凑模式（--compact）：22 工具（21 领域工具 + 1 `batch_execute`）

## 近期完成的工作

### 第九阶段：紧凑模式（本次会话）
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
1. **端到端连通性测试**：启动 Godot + Python server，验证 Cline 能否成功调用工具
2. **跟进上游新版本**：监控 upstream 是否有新 commit 需要合并
3. 可选：编写自动化测试

## 重要决策记录
- Python server 作为 WS **Server**（监听端），Godot 作为 WS **Client**（连接端）
- `--compact` 模式通过命令行参数启用，不使用环境变量
- 紧凑模式纯 Python 层面实现（`compact.py` 是分发器），零 GDScript 改动
- 紧凑模式使用 `action:str` + `params:dict` 统一签名，docstring 列出所有可用 action 及参数类型
- 工具总数 175（完整模式）/ 22（紧凑模式），与 upstream README 一致
- `GODOT_MCP_PORT` 仅决定起始端口偏好，始终启用端口重试（6505-6514）

## 重要模式与偏好
- 路径信息在文档中**一律脱敏**（使用 `<APPDATA>`、`<项目根目录>` 等占位符）
- 未经验证的事项显式标注 `⚠️`
- 中文作为项目文档和 Cline 交互的主要语言