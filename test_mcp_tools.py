"""
MCP 工具连接测试脚本
用途：在没有 Claude API Key 的情况下，测试 6000-6007 端口的 MCP 服务是否正常工作
"""
import asyncio
import sys
from mcp_sdk import GiiispMCPClient

# Windows 控制台 UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        import io
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


async def test_mcp_services():
    """测试所有 MCP 服务的连通性"""

    print("\n" + "="*80)
    print("🔧 MCP 服务连接测试")
    print("="*80)
    print("说明：此测试不需要 Claude API Key，仅测试 MCP 服务是否正常运行\n")

    # 定义测试用例
    test_cases = [
        {
            "port": 6000,
            "name": "Crossref",
            "tool": "search_works",
            "args": {"query": "Machine Learning", "rows": 1},
            "description": "搜索学术文献元数据"
        },
        {
            "port": 6001,
            "name": "BioC",
            "tool": "get_article_info",
            "args": {"id": "PMC7095368"},
            "description": "获取 PubMed Central 文献"
        },
        {
            "port": 6002,
            "name": "DeepResearch",
            "tool": "DeepResearch",
            "args": {"searchQuery": "LLM", "count": 1},
            "description": "集思谱深度研究引擎"
        },
        {
            "port": 6003,
            "name": "Arxiv Abstract",
            "tool": "searchArxivByAbstract",
            "args": {"key": "GPT", "pageSize": 1},
            "description": "通过摘要搜索 arXiv"
        },
        {
            "port": 6004,
            "name": "OpenLibrary",
            "tool": "searchBooks",
            "args": {"query": "Deep Learning", "limit": 1},
            "description": "搜索图书信息"
        },
        {
            "port": 6005,
            "name": "Entrez",
            "tool": "ESearch",
            "args": {"db": "pubmed", "term": "covid", "retmax": 1},
            "description": "搜索 NCBI 数据库"
        },
        {
            "port": 6006,
            "name": "Arxiv ID",
            "tool": "SearchByArxivNo",
            "args": {"key": "1706.03762"},
            "description": "通过 ID 查找 arXiv 论文"
        },
        {
            "port": 6007,
            "name": "Arxiv Title",
            "tool": "searchArxivByTitle",
            "args": {"key": "Attention Is All You Need"},
            "description": "通过标题搜索 arXiv"
        }
    ]

    results = []

    for idx, test in enumerate(test_cases, 1):
        print(f"\n[{idx}/{len(test_cases)}] 测试 {test['name']} (端口 {test['port']})")
        print(f"    功能: {test['description']}")
        print(f"    工具: {test['tool']}")

        try:
            client = GiiispMCPClient(port=test['port'], service_name=test['name'])
            data = await client.call_tool(test['tool'], test['args'])

            if data:
                print(f"    ✅ 测试通过 - 成功获取数据")
                results.append({"name": test['name'], "status": "✅ 通过", "port": test['port']})
            else:
                print(f"    ⚠️ 测试警告 - 连接成功但未返回数据")
                results.append({"name": test['name'], "status": "⚠️ 无数据", "port": test['port']})

        except Exception as e:
            print(f"    ❌ 测试失败 - {str(e)}")
            results.append({"name": test['name'], "status": f"❌ 失败: {str(e)[:30]}", "port": test['port']})

        print("-" * 80)

    # 汇总报告
    print("\n" + "="*80)
    print("📊 测试结果汇总")
    print("="*80)

    passed = sum(1 for r in results if "✅" in r['status'])
    total = len(results)

    print(f"\n总计: {passed}/{total} 个服务测试通过\n")

    for result in results:
        print(f"  端口 {result['port']:4d} | {result['name']:20s} | {result['status']}")

    print("\n" + "="*80)

    if passed == total:
        print("🎉 所有 MCP 服务运行正常！")
        print("💡 下一步：配置 ANTHROPIC_API_KEY 后运行 claude_agent.py")
    elif passed > 0:
        print(f"⚠️ 部分服务异常，请检查失败的服务")
    else:
        print("❌ 所有服务均无法连接，请检查：")
        print("   1. MCP 服务是否已启动")
        print("   2. 端口 6000-6007 是否被占用")
        print("   3. 防火墙设置是否阻止连接")

    print("="*80 + "\n")


async def test_single_service(port: int):
    """测试单个服务（用于调试）"""

    service_map = {
        6000: ("Crossref", "search_works", {"query": "AI", "rows": 1}),
        6002: ("DeepResearch", "DeepResearch", {"searchQuery": "LLM", "count": 1}),
        6003: ("Arxiv", "searchArxivByAbstract", {"key": "GPT", "pageSize": 1}),
    }

    if port not in service_map:
        print(f"❌ 端口 {port} 未配置测试用例")
        return

    name, tool, args = service_map[port]

    print(f"\n🔍 测试单个服务: {name} (端口 {port})")
    print(f"工具: {tool}")
    print(f"参数: {args}\n")

    client = GiiispMCPClient(port=port, service_name=name)
    data = await client.call_tool(tool, args)

    if data:
        import json
        print("\n✅ 成功获取数据:")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
    else:
        print("\n❌ 未获取到数据")


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # 检查命令行参数
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            asyncio.run(test_single_service(port))
        except ValueError:
            print("❌ 错误: 端口号必须是数字")
            print("用法: python test_mcp_tools.py [端口号]")
            print("示例: python test_mcp_tools.py 6002")
    else:
        # 运行完整测试
        asyncio.run(test_mcp_services())
