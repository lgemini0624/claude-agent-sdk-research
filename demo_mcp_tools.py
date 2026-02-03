"""
MCP 工具演示 - 不需要 Claude API
展示如何使用 MCP 工具获取学术数据并生成报告
"""
import asyncio
import json
import sys
import datetime
from mcp_sdk import GiiispMCPClient

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

async def demo_mcp_tools():
    """演示 MCP 工具的使用（不需要 Claude API）"""

    print("\n" + "="*80)
    print("🔬 MCP 学术搜索工具演示")
    print("="*80)
    print("说明：此演示展示如何使用 6000-6007 端口的 MCP 服务获取学术数据")
    print("="*80)

    all_papers = []

    # 1. DeepResearch - 综合搜索
    print("\n[1/3] 🔍 使用 DeepResearch 搜索 'Large Language Models'...")
    client1 = GiiispMCPClient(6002, "DeepResearch")
    data1 = await client1.call_tool("DeepResearch", {"searchQuery": "Large Language Models", "count": 5})

    if data1:
        papers = data1.get("data", {}).get("data", [])
        for paper in papers:
            if isinstance(paper, dict):
                all_papers.append({
                    "source": "DeepResearch (集思谱)",
                    "title": paper.get("title", "未知标题"),
                    "authors": paper.get("authors", "未知作者"),
                    "year": paper.get("year", "未知年份"),
                    "doi": paper.get("doi", ""),
                    "abstract": paper.get("abstractText", "暂无摘要")[:200] + "...",
                    "url": paper.get("link") or paper.get("doi") or "#"
                })
        print(f"   ✅ 找到 {len(papers)} 篇论文")

    # 2. arXiv Abstract Search
    print("\n[2/3] 📚 使用 arXiv 搜索 'GPT' 相关论文...")
    client2 = GiiispMCPClient(6003, "Arxiv Abstract")
    data2 = await client2.call_tool("searchArxivByAbstract", {"key": "GPT", "pageSize": 5})

    if data2:
        papers = data2.get("data", {}).get("data", [])
        for paper in papers:
            if isinstance(paper, dict):
                arxiv_id = paper.get("arxivNo") or paper.get("arvixNo", "")
                if "arXiv:" in str(arxiv_id):
                    arxiv_id = arxiv_id.replace("arXiv:", "")

                all_papers.append({
                    "source": "arXiv (预印本)",
                    "title": paper.get("title", "未知标题"),
                    "authors": paper.get("authors", "未知作者"),
                    "year": paper.get("year", "未知年份"),
                    "arxiv_id": arxiv_id,
                    "abstract": paper.get("paperAbstract", "暂无摘要")[:200] + "...",
                    "url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "#"
                })
        print(f"   ✅ 找到 {len(papers)} 篇论文")

    # 3. Crossref - 学术文献元数据
    print("\n[3/3] 📖 使用 Crossref 搜索 'Transformer' 相关论文...")
    client3 = GiiispMCPClient(6000, "Crossref")
    data3 = await client3.call_tool("search_works", {"query": "Transformer neural network", "rows": 5})

    if data3:
        items = data3.get("message", {}).get("items", [])
        for item in items:
            if isinstance(item, dict):
                all_papers.append({
                    "source": "Crossref (元数据)",
                    "title": item.get("title", ["未知标题"])[0] if item.get("title") else "未知标题",
                    "authors": ", ".join([f"{a.get('given', '')} {a.get('family', '')}"
                                         for a in item.get("author", [])[:3]]),
                    "year": item.get("published", {}).get("date-parts", [[None]])[0][0],
                    "doi": item.get("DOI", ""),
                    "url": item.get("URL", "#")
                })
        print(f"   ✅ 找到 {len(items)} 篇论文")

    # 生成报告
    print("\n" + "="*80)
    print("📊 数据汇总")
    print("="*80)
    print(f"总计找到 {len(all_papers)} 篇相关论文\n")

    # 保存为 Markdown
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"MCP_Demo_Report_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# 📑 Large Language Models 学术调研报告\n\n")
        f.write(f"**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**数据来源**: DeepResearch, arXiv, Crossref\n\n")
        f.write(f"**论文总数**: {len(all_papers)}\n\n")
        f.write("---\n\n")

        for idx, paper in enumerate(all_papers, 1):
            f.write(f"## {idx}. {paper['title']}\n\n")
            f.write(f"- **来源**: {paper['source']}\n")
            if paper.get('authors'):
                f.write(f"- **作者**: {paper['authors']}\n")
            if paper.get('year'):
                f.write(f"- **年份**: {paper['year']}\n")
            if paper.get('doi'):
                f.write(f"- **DOI**: {paper['doi']}\n")
            if paper.get('arxiv_id'):
                f.write(f"- **arXiv ID**: {paper['arxiv_id']}\n")
            f.write(f"- **链接**: [查看原文]({paper['url']})\n")
            if paper.get('abstract'):
                f.write(f"\n**摘要**:\n> {paper['abstract']}\n")
            f.write("\n---\n\n")

    print(f"✅ 报告已生成: {filename}")
    print("\n" + "="*80)
    print("💡 说明")
    print("="*80)
    print("此演示展示了如何使用 MCP 工具获取学术数据。")
    print("在实际的 claude_agent.py 中，Claude 会：")
    print("  1. 自主决定调用哪些工具")
    print("  2. 观察返回的数据")
    print("  3. 动态调整搜索策略")
    print("  4. 智能整合多个数据源")
    print("  5. 生成更专业的综述报告")
    print("\n如果你的 API 连接问题解决后，可以运行 claude_agent.py 体验完整功能。")
    print("="*80)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(demo_mcp_tools())
