# Claude 自主学术研究代理 使用指南

## 🚀 快速开始

### 1. 配置 API Key

**方式一：创建 .env 文件（推荐）**

在项目目录下创建 `.env` 文件，内容如下：

```
ANTHROPIC_API_KEY=sk-ant-api03-你的完整API密钥
```

**注意事项：**
- 不要有多余的空格、引号或换行
- 确保 Key 完整（通常 100+ 字符）
- 文件名必须是 `.env`（不是 `.env.txt`）

**方式二：设置环境变量**

Windows PowerShell:
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-api03-你的完整API密钥"
```

Windows CMD:
```cmd
set ANTHROPIC_API_KEY=sk-ant-api03-你的完整API密钥
```

Linux/Mac:
```bash
export ANTHROPIC_API_KEY=sk-ant-api03-你的完整API密钥
```

### 2. 获取 API Key

访问 [Anthropic Console](https://console.anthropic.com) 注册并获取 API Key。

如果使用中转服务，还需要在 `.env` 中添加：
```
ANTHROPIC_BASE_URL=https://你的中转地址/v1
```

### 3. 运行代理

```bash
python claude_agent.py
```

## 📋 功能说明

### 核心特性

1. **工具自动注册**: 将 6000-6007 端口的 MCP 服务自动注册为 Claude 工具
2. **智能决策**: Claude 自主决定调用哪些工具、以什么顺序调用
3. **数据融合**: 自动整合来自不同数据源的结果
4. **闭环执行**: 观察工具返回结果，动态调整下一步行动

### 可用工具

| 端口 | 工具名称 | 功能描述 |
|------|---------|---------|
| 6000 | Crossref | 搜索学术文献元数据（DOI、引用等） |
| 6001 | BioC | 获取 PubMed Central 生物医学文献 |
| 6002 | DeepResearch | 集思谱深度研究引擎（综合搜索） |
| 6003 | Arxiv Abstract | 通过摘要关键词搜索 arXiv 论文 |
| 6004 | OpenLibrary | 搜索图书信息 |
| 6005 | Entrez | 搜索 NCBI 数据库（PubMed 等） |
| 6006 | Arxiv ID | 通过 arXiv ID 精确查找论文 |
| 6007 | Arxiv Title | 通过标题搜索 arXiv 论文 |

## 🎯 使用示例

### 示例 1: 生成综述报告（默认）

直接运行 `python claude_agent.py`，会生成关于 Large Language Models 的综述报告。

### 示例 2: 自定义研究主题

修改 `claude_agent.py` 中的 `instruction` 变量：

```python
instruction = """
请帮我调研 Transformer 架构的演进历史，
重点关注 Attention 机制的改进。
要求：
1. 找出 5-10 篇关键论文
2. 按时间顺序排列
3. 说明每篇论文的核心创新点
"""
```

### 示例 3: 编程调用

```python
from claude_agent import ClaudeAcademicAgent
import asyncio

async def my_research():
    agent = ClaudeAcademicAgent()

    result = await agent.run(
        "请搜索关于 BERT 模型的最新研究进展",
        max_iterations=10
    )

    print(result)

asyncio.run(my_research())
```

## 🔧 高级配置

### 调整最大迭代次数

```python
result = await agent.run(instruction, max_iterations=20)  # 默认 10
```

### 使用不同的 Claude 模型

修改 `claude_agent.py` 第 293 行：

```python
model="claude-opus-4-5-20251101",  # 使用 Opus 4.5（更强大但更贵）
```

可选模型：
- `claude-3-5-sonnet-20241022` (默认，性价比高)
- `claude-opus-4-5-20251101` (最强大)
- `claude-3-5-haiku-20241022` (最快最便宜)

## ⚠️ 常见问题

### 1. 认证失败 (401 错误)

**原因**: API Key 无效或格式错误

**解决方案**:
- 检查 `.env` 文件中的 Key 是否完整
- 确认没有多余的空格、引号或换行
- 到 Anthropic Console 重新生成 Key
- 检查账户余额是否充足

### 2. 连接超时

**原因**: 网络问题或 MCP 服务未启动

**解决方案**:
- 确认 6000-6007 端口的 MCP 服务正在运行
- 检查防火墙设置
- 如果使用中转 API，检查 `ANTHROPIC_BASE_URL` 是否正确

### 3. 工具调用失败

**原因**: MCP 服务返回错误或数据格式不匹配

**解决方案**:
- 查看控制台输出的详细错误信息
- 单独测试对应端口的 MCP 服务
- 检查 `mcp_sdk.py` 中的工具名称是否正确

### 4. 达到最大迭代次数

**原因**: 任务太复杂或 Claude 陷入循环

**解决方案**:
- 增加 `max_iterations` 参数
- 简化任务指令，分步执行
- 检查是否有工具持续返回空结果

## 📊 输出说明

程序会生成 `LLM_Survey_by_Claude.md` 文件，包含：
- 论文标题、作者、发表年份
- 核心贡献和创新点
- 论文链接（DOI、arXiv 等）
- 按主题或时间分类的结构化内容

## 🔄 工作流程

```
用户指令
    ↓
Claude 分析任务
    ↓
决定调用哪个工具 → 执行 MCP 调用 → 获取数据
    ↓                                      ↓
观察结果 ←─────────────────────────────────┘
    ↓
决定下一步（继续调用工具 or 生成报告）
    ↓
输出最终结果
```

## 💡 最佳实践

1. **明确任务目标**: 给 Claude 清晰的指令和要求
2. **合理设置迭代次数**: 复杂任务建议 15-20 次
3. **监控工具调用**: 观察 Claude 的决策过程，优化指令
4. **数据源选择**: 不同领域选择合适的工具（生物医学用 Entrez，AI 用 arXiv）
5. **结果验证**: 检查生成的报告，必要时手动补充

## 📝 许可证

MIT License
