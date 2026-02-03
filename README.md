# Claude Agent SDK 调研项目

基于 Claude API 的自主学术研究代理，实现从硬编码流程到 AI 自主决策的升级。

## 🎯 项目简介

本项目展示如何使用 Claude Tool Use API 将多个 MCP (Model Context Protocol) 服务注册为 Claude 工具，让 AI 自主决定调用哪些工具来完成复杂任务。

**核心特性**：
- ✅ **自主决策**：Claude 根据任务自动选择工具组合
- ✅ **闭环执行**：观察数据后动态调整策略
- ✅ **智能整合**：自动融合多个数据源
- ✅ **可扩展**：添加新工具只需配置

## 📁 项目结构

```
MCP_DOCUMENTATION/
├── claude_agent.py              # Claude 自主代理（核心）
├── mcp_sdk.py                   # MCP 客户端 SDK
├── demo_mcp_tools.py            # MCP 工具演示（无需 API）
├── test_mcp_tools.py            # 服务测试脚本
├── quick_test.py                # 快速测试
├── Claude_Agent_SDK_调研报告.md  # 完整调研报告
├── README_CLAUDE_AGENT.md       # 详细使用指南
├── 项目说明.md                   # 架构说明
├── .env.example                 # API Key 配置示例
├── .gitignore                   # Git 忽略文件
└── 00-07text/                   # MCP 服务测试文件
```

## 🚀 快速开始

### 1. 配置 API Key

创建 `.env` 文件：

```bash
ANTHROPIC_API_KEY=sk-ant-api03-你的API密钥
```

### 2. 安装依赖

```bash
pip install anthropic mcp
```

### 3. 测试 MCP 服务（可选）

```bash
# 快速测试单个服务
python quick_test.py

# 测试所有服务
python test_mcp_tools.py

# 演示多工具整合（无需 Claude API）
python demo_mcp_tools.py
```

### 4. 运行 Claude 自主代理

```bash
python claude_agent.py
```

## 💡 核心概念

### 从硬编码到自主决策

**❌ 旧方式（硬编码）**：
```python
task1 = client.call_tool("DeepResearch", {...})
task2 = client.call_tool("arxiv", {...})
results = await gather(task1, task2)
# 手动处理和整合数据...
```

**✅ 新方式（自主决策）**：
```python
instruction = """
请综合利用所有学术搜索工具，
生成关于 Large Language Models 的综述报告。
"""
result = await agent.run(instruction)
```

### 工作流程

```
用户指令 → Claude 分析 → 决定调用工具 → 执行 MCP 调用
    ↑                                            ↓
    └──────── 观察结果，决定下一步 ←──────────────┘
```

## 🛠️ 可用工具

| 端口 | 工具名称 | 功能 |
|------|---------|------|
| 6000 | Crossref | 搜索学术文献元数据 |
| 6001 | BioC | 获取 PubMed Central 文献 |
| 6002 | DeepResearch | 集思谱综合搜索 |
| 6003 | Arxiv Abstract | 通过摘要搜索 arXiv |
| 6004 | OpenLibrary | 搜索图书信息 |
| 6005 | Entrez | 搜索 NCBI 数据库 |
| 6006 | Arxiv ID | 通过 ID 查找 arXiv 论文 |
| 6007 | Arxiv Title | 通过标题搜索 arXiv |

## 📚 文档

- **[完整调研报告](Claude_Agent_SDK_调研报告.md)** - 技术架构、实现细节、问题解决
- **[使用指南](README_CLAUDE_AGENT.md)** - 配置方法、使用示例、常见问题
- **[项目说明](项目说明.md)** - 文件结构、工作原理、性能对比

## 🎓 技术亮点

1. **工具映射机制** - 将 8 个 MCP 服务注册为 Claude 工具
2. **自主决策循环** - 实现 Claude 的闭环执行逻辑
3. **MCP 客户端封装** - 统一的服务调用接口
4. **模块化设计** - SDK、工具定义、决策循环相互独立

## ⚠️ 注意事项

- 需要 Anthropic API Key（官方或中转 API）
- MCP 服务需要在 6000-6007 端口运行
- 建议先运行 `demo_mcp_tools.py` 测试基础功能

## 📊 代码统计

| 文件 | 行数 | 功能 |
|------|------|------|
| `claude_agent.py` | ~490 | Claude 代理核心逻辑 |
| `mcp_sdk.py` | ~70 | MCP 客户端封装 |
| `demo_mcp_tools.py` | ~150 | 工具演示脚本 |
| `test_mcp_tools.py` | ~120 | 服务测试脚本 |

## 🔗 相关资源

- [Anthropic API 文档](https://docs.anthropic.com)
- [Claude Tool Use 指南](https://docs.anthropic.com/claude/docs/tool-use)
- [Model Context Protocol](https://modelcontextprotocol.io)


[你的名字] - Claude Agent SDK 调研项目

---

**如有问题，请查看详细文档或提交 Issue。**
