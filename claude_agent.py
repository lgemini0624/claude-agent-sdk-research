"""
Claude 自主学术研究代理
功能：将 MCP 服务注册为 Claude 工具，让 Claude 自主决定调用哪些服务来完成任务
"""
import asyncio
import json
import os
import sys
from typing import List, Dict, Any

# Windows 控制台 UTF-8，避免 emoji/中文 报错
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        import io
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from anthropic import Anthropic, AuthenticationError
from mcp_sdk import GiiispMCPClient


class ClaudeAcademicAgent:
    """基于 Claude API 的自主学术研究代理"""

    def __init__(self, api_key: str = None, base_url: str = None):
        """
        初始化 Claude 代理
        :param api_key: Anthropic API Key (如果不提供，会从环境变量 ANTHROPIC_API_KEY 读取)
        :param base_url: 中转/代理 API 地址；sk- 开头的 Key 必须指定，否则用环境变量 ANTHROPIC_BASE_URL
        """
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        url = base_url or os.environ.get("ANTHROPIC_BASE_URL", "https://api.580ai.net/v1")
        self.client = Anthropic(api_key=key, base_url=url)
        self.conversation_history = []

        # 初始化所有 MCP 客户端
        self.mcp_clients = {
            "crossref": GiiispMCPClient(6000, "Crossref"),
            "bioc": GiiispMCPClient(6001, "BioC"),
            "deep_research": GiiispMCPClient(6002, "DeepResearch"),
            "arxiv_abstract": GiiispMCPClient(6003, "Arxiv Abstract"),
            "openlibrary": GiiispMCPClient(6004, "OpenLibrary"),
            "entrez": GiiispMCPClient(6005, "Entrez"),
            "arxiv_id": GiiispMCPClient(6006, "Arxiv ID"),
            "arxiv_title": GiiispMCPClient(6007, "Arxiv Title"),
        }

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        定义所有可用工具的规范
        这是关键：将你的 MCP 服务转换为 Claude 可以理解的工具格式
        """
        return [
            {
                "name": "crossref_search",
                "description": "搜索学术文献的元数据（标题、作者、DOI、引用次数等）。适合查找已发表的期刊论文和会议论文。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词，例如 'Machine Learning' 或 'Neural Networks'"
                        },
                        "rows": {
                            "type": "integer",
                            "description": "返回结果数量，默认 5",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "bioc_get_article",
                "description": "从 PubMed Central 获取生物医学文献的详细信息（全文、作者、摘要等）。需要提供 PMC ID。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "PubMed Central ID，例如 'PMC7095368'"
                        }
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "deep_research",
                "description": "使用集思谱（Giiisp）的深度研究引擎，搜索高质量学术论文。返回论文标题、摘要、DOI、引用等信息。这是最强大的综合搜索工具。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "searchQuery": {
                            "type": "string",
                            "description": "搜索查询，例如 'Large Language Models' 或 'Transformer Architecture'"
                        },
                        "count": {
                            "type": "integer",
                            "description": "返回结果数量，默认 10",
                            "default": 10
                        }
                    },
                    "required": ["searchQuery"]
                }
            },
            {
                "name": "arxiv_search_by_abstract",
                "description": "在 arXiv 预印本库中通过摘要关键词搜索论文。适合查找最新的研究成果（尤其是 AI/ML 领域）。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "摘要中的关键词，例如 'GPT' 或 'attention mechanism'"
                        },
                        "pageSize": {
                            "type": "integer",
                            "description": "返回结果数量，默认 10",
                            "default": 10
                        }
                    },
                    "required": ["key"]
                }
            },
            {
                "name": "openlibrary_search",
                "description": "搜索图书信息（书名、作者、出版年份、ISBN 等）。适合查找学术书籍和教材。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词，例如 'Deep Learning' 或作者名 'Ian Goodfellow'"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回结果数量，默认 5",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "entrez_search",
                "description": "搜索 NCBI 数据库（PubMed、GenBank、Protein 等）。适合生物医学和生命科学领域的文献检索。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "db": {
                            "type": "string",
                            "description": "数据库名称，例如 'pubmed'、'pmc'、'nucleotide'",
                            "enum": ["pubmed", "pmc", "nucleotide", "protein", "gene"]
                        },
                        "term": {
                            "type": "string",
                            "description": "搜索词，例如 'CRISPR' 或 'COVID-19'"
                        },
                        "retmax": {
                            "type": "integer",
                            "description": "返回结果数量，默认 10",
                            "default": 10
                        }
                    },
                    "required": ["db", "term"]
                }
            },
            {
                "name": "arxiv_search_by_id",
                "description": "通过 arXiv ID 精确查找论文的详细信息。当你已知论文的 arXiv 编号时使用。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "arXiv ID，例如 '1706.03762' (Attention Is All You Need)"
                        }
                    },
                    "required": ["key"]
                }
            },
            {
                "name": "arxiv_search_by_title",
                "description": "通过论文标题在 arXiv 中搜索。适合当你知道论文的大致标题时使用。",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "论文标题或标题关键词，例如 'Attention Is All You Need'"
                        }
                    },
                    "required": ["key"]
                }
            }
        ]

    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        执行工具调用
        这是桥接层：将 Claude 的工具调用请求转换为实际的 MCP 调用
        """
        print(f"\n🔧 [工具执行] {tool_name}")
        print(f"   参数: {json.dumps(tool_input, ensure_ascii=False)}")

        try:
            # 根据工具名称路由到对应的 MCP 客户端
            if tool_name == "crossref_search":
                result = await self.mcp_clients["crossref"].call_tool(
                    "search_works",
                    {"query": tool_input["query"], "rows": tool_input.get("rows", 5)}
                )

            elif tool_name == "bioc_get_article":
                result = await self.mcp_clients["bioc"].call_tool(
                    "get_article_info",
                    {"id": tool_input["id"]}
                )

            elif tool_name == "deep_research":
                result = await self.mcp_clients["deep_research"].call_tool(
                    "DeepResearch",
                    {"searchQuery": tool_input["searchQuery"], "count": tool_input.get("count", 10)}
                )

            elif tool_name == "arxiv_search_by_abstract":
                result = await self.mcp_clients["arxiv_abstract"].call_tool(
                    "searchArxivByAbstract",
                    {"key": tool_input["key"], "pageSize": tool_input.get("pageSize", 10)}
                )

            elif tool_name == "openlibrary_search":
                result = await self.mcp_clients["openlibrary"].call_tool(
                    "searchBooks",
                    {"query": tool_input["query"], "limit": tool_input.get("limit", 5)}
                )

            elif tool_name == "entrez_search":
                result = await self.mcp_clients["entrez"].call_tool(
                    "ESearch",
                    {
                        "db": tool_input["db"],
                        "term": tool_input["term"],
                        "retmax": tool_input.get("retmax", 10)
                    }
                )

            elif tool_name == "arxiv_search_by_id":
                result = await self.mcp_clients["arxiv_id"].call_tool(
                    "SearchByArxivNo",
                    {"key": tool_input["key"]}
                )

            elif tool_name == "arxiv_search_by_title":
                result = await self.mcp_clients["arxiv_title"].call_tool(
                    "searchArxivByTitle",
                    {"key": tool_input["key"]}
                )

            else:
                return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)

            # 将结果转换为字符串返回给 Claude
            if result:
                print(f"   ✅ 成功获取数据")
                return json.dumps(result, ensure_ascii=False, indent=2)
            else:
                print(f"   ⚠️ 未获取到数据")
                return json.dumps({"error": "未获取到数据"}, ensure_ascii=False)

        except Exception as e:
            print(f"   ❌ 执行失败: {str(e)}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def run(self, user_instruction: str, max_iterations: int = 10) -> str:
        """
        运行 Claude 代理的主循环
        :param user_instruction: 用户指令，例如 "请综合利用所有工具，为我生成一份关于 Large Language Models 的严谨综述"
        :param max_iterations: 最大迭代次数，防止无限循环
        :return: Claude 的最终回复
        """
        print("\n" + "="*80)
        print("🤖 Claude 自主研究代理启动")
        print("="*80)
        print(f"📝 用户指令: {user_instruction}")
        print("="*80)

        # 初始化对话
        self.conversation_history = [
            {
                "role": "user",
                "content": user_instruction
            }
        ]

        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 [迭代 {iteration}/{max_iterations}]")

            # 调用 Claude API
            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet",  # 中转 API 通用名称
                    max_tokens=4096,
                    tools=self.get_tool_definitions(),
                    messages=self.conversation_history
                )
            except AuthenticationError:
                print("\n❌ 认证失败 (401 无效的令牌)")
                print("   请检查 ANTHROPIC_API_KEY：")
                print("   1. 在 https://console.anthropic.com 登录并复制正确的 API Key")
                print("   2. 确认 .env 或环境变量中只包含 key，无多余空格/换行/引号")
                print("   3. 若 key 已过期或已撤销，请重新生成后再试")
                print("   4. 若账户余额不足，请到 Plans & Billing 充值")
                raise

            print(f"   停止原因: {response.stop_reason}")

            # 处理响应
            if response.stop_reason == "end_turn":
                # Claude 完成了任务，返回最终结果
                final_text = ""
                for block in response.content:
                    if block.type == "text":
                        final_text += block.text

                print("\n" + "="*80)
                print("✅ Claude 已完成任务")
                print("="*80)
                return final_text

            elif response.stop_reason == "tool_use":
                # Claude 决定使用工具
                assistant_message = {"role": "assistant", "content": response.content}
                self.conversation_history.append(assistant_message)

                # 执行所有工具调用
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"\n   🎯 Claude 决定调用: {block.name}")

                        # 执行工具
                        result = await self.execute_tool(block.name, block.input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                # 将工具结果返回给 Claude
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })

            else:
                # 其他停止原因（如 max_tokens）
                print(f"\n⚠️ 意外停止: {response.stop_reason}")
                break

        print("\n⚠️ 达到最大迭代次数，任务可能未完成")
        return "任务未完成（达到最大迭代次数）"


def _trim_api_key(value: str) -> str:
    """仅去掉 BOM、首尾空白和引号，不删 Key 内任何字符"""
    if not value:
        return ""
    return value.replace("\ufeff", "").strip().strip('"').strip("'")


def _load_env_file():
    """从脚本目录或当前工作目录的 .env 加载 ANTHROPIC_API_KEY，.env 优先覆盖环境变量"""
    tried = []
    for base in [os.path.dirname(os.path.abspath(__file__)), os.getcwd()]:
        env_path = os.path.join(base, ".env")
        tried.append(env_path)
        if not os.path.isfile(env_path):
            continue
        try:
            with open(env_path, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ANTHROPIC_API_KEY=") and "=" in line:
                        _, _, value = line.partition("=")
                        value = _trim_api_key(value)
                        if value:
                            os.environ["ANTHROPIC_API_KEY"] = value
                            print(f"🔑 [调试信息] 已从 .env 加载 Key，路径: {env_path}")
                        return
        except Exception:
            pass
    print(f"🔑 [调试信息] 未找到 .env（已尝试: {tried[0]}, {tried[1]}），使用环境变量中的 ANTHROPIC_API_KEY")


async def main():
    """示例：让 Claude 自主完成学术综述任务"""

    # 始终先加载 .env，避免系统里旧的短 Key 覆盖 .env 里的完整 Key
    _load_env_file()

    # 检查 API Key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n" + "="*80)
        print("❌ 错误: 未找到 ANTHROPIC_API_KEY")
        print("="*80)
        print("\n📋 配置方法：")
        print("\n方式一：创建 .env 文件（推荐）")
        print("   1. 在当前目录创建文件名为 .env 的文件")
        print("   2. 文件内容一行：ANTHROPIC_API_KEY=你的完整key")
        print("   3. 示例：ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...")
        print("\n方式二：设置环境变量")
        print("   PowerShell: $env:ANTHROPIC_API_KEY=\"你的key\"")
        print("   CMD:        set ANTHROPIC_API_KEY=你的key")
        print("\n🔑 获取 API Key:")
        print("   访问 https://console.anthropic.com 注册并获取")
        print("\n💡 提示：已创建 .env.example 作为参考")
        print("="*80)
        return

    # 只做最小整理：去 BOM、首尾空白和引号，不删 Key 内任何字符
    raw_key = os.environ.get("ANTHROPIC_API_KEY", "")
    api_key = _trim_api_key(raw_key)
    os.environ["ANTHROPIC_API_KEY"] = api_key

    # === 调试：确认程序读到的 Key ===
    print(f"\n🔑 [调试信息] Key 长度: {len(api_key)}")
    if len(api_key) > 10:
        print(f"🔑 [调试信息] Key 预览: {api_key[:7]}...{api_key[-4:]}")
    else:
        print("❌ [调试信息] Key 太短！请确认 .env 在脚本同目录且内容为一行 ANTHROPIC_API_KEY=你的完整key")
    # =====================

    if not api_key:
        print("❌ 错误: ANTHROPIC_API_KEY 为空")
        return

    if len(api_key) < 20:
        print("❌ 错误: Key 长度不足，无法发起认证")
        print("   请检查 .env：整行应为 ANTHROPIC_API_KEY=你的完整key（无换行、无引号、无空格）")
        return

    # 创建代理
    agent = ClaudeAcademicAgent()

    # 给 Claude 一个高层指令，让它自主决定如何完成
    instruction = """
请综合利用 6000-6007 端口的所有学术搜索工具，为我生成一份关于 Large Language Models (大语言模型) 的严谨综述报告。

要求：
1. 使用多个数据源（arXiv、Crossref、DeepResearch 等）进行全面检索
2. 重点关注 2020 年后的重要论文（如 GPT、BERT、Transformer 等）
3. 整理出至少 10 篇高质量论文
4. 对每篇论文提供：标题、作者、发表年份、核心贡献、链接
5. 按照时间顺序或主题分类组织内容
6. 最后生成 Markdown 格式的报告

请自主决定调用哪些工具、以什么顺序调用，以及如何整合数据。
"""

    # 运行代理
    result = await agent.run(instruction, max_iterations=15)

    # 保存结果
    output_file = "LLM_Survey_by_Claude.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"\n📄 报告已保存到: {output_file}")
    print("\n" + "="*80)
    print("预览:")
    print("="*80)
    print(result[:500] + "..." if len(result) > 500 else result)


if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
