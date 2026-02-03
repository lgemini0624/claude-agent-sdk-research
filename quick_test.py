"""
快速测试脚本 - 测试单个 MCP 服务
"""
import asyncio
import sys
from mcp_sdk import GiiispMCPClient

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

async def quick_test():
    print("\n测试 DeepResearch 服务 (端口 6002)...")

    client = GiiispMCPClient(6002, "DeepResearch")
    result = await client.call_tool("DeepResearch", {"searchQuery": "LLM", "count": 1})

    if result:
        print("✅ 测试成功！")
        print(f"返回数据类型: {type(result)}")
    else:
        print("❌ 测试失败")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(quick_test())
