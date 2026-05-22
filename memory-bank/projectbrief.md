# 项目概要

## 项目名称
Godot MCP Pro（Python Fork）

## 仓库信息
- **origin**: `a690089735/godot-mcp-pro`（本 fork）
- **upstream**: `youichi-uda/godot-mcp-pro`（原始仓库，付费 Node.js 版本）

## 项目定位
将上游付费的 Node.js/TypeScript MCP Server 替换为**免费开源的 Python FastMCP Server**，同时保持与上游 Godot 插件（GDScript addon）的完全兼容。

## 核心目标
1. 让 AI 编程助手（Cline、Claude Code 等）通过 MCP 协议直接操控 Godot 4.x 编辑器
2. 提供与上游 Node.js 服务器功能对等的 Python 替代方案
3. 持续跟进上游 addon 更新，保持 GDScript 端同步

## 项目范围
- ✅ Python FastMCP Server（替代 Node.js）
- ✅ 上游 Godot addon 插件（GDScript，原样使用）
- ✅ Cline/Claude Desktop 等 MCP 客户端配置
- ❌ 不包含上游的 CLI 工具（`build/cli.js`）
- ❌ 不包含上游的 HTTP transport 模式
- ❌ 不包含上游的 `--lite`/`--minimal`/`--3d` 模式过滤

## 与上游的关系
- 上游 addon（`addons/godot_mcp/`）通过定期 merge 保持同步
- Python server（`server/`）是本 fork 独有的实现
- 上游的 `server/` 目录（Node.js/TypeScript）在付费包中，本 fork 用 Python 完全替代