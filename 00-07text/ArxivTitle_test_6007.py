import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

# ==========================================
# ⚙️ 配置区域 (Configuration)
# 🎯 目标：测试 Arxiv Title 服务 (端口 6007)
# ==========================================
TARGET_PORT = 6007
SERVICE_NAME = "Giiisp Search By Title"
SERVER_URL = f"http://giiisp.com:{TARGET_PORT}/sse"

TEST_CASE = {
    # ⚠️ 注意：文档里这个工具名是小写开头的！
    "tool_name": "searchArxivByTitle",
    "params": {
        "key": "Attention Is All You Need",
        "pageSize": 1
    }
}
# ==========================================

async def run_standard_test():
    print(f"🚀 [启动测试] 服务: {SERVICE_NAME} | 端口: {TARGET_PORT}")
    try:
        async with sse_client(SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools = await session.list_tools()
                available_tools = [t.name for t in tools.tools]
                print(f"✅ 连接成功 | 发现工具: {available_tools}")
                
                target = TEST_CASE["tool_name"]
                if target not in available_tools:
                    print(f"❌ [名称不匹配] 预期: '{target}' | 实际: {available_tools}")
                    return

                print(f"🔍 正在按标题搜索 ...")
                result = await session.call_tool(name=target, arguments=TEST_CASE["params"])
                
                for content in result.content:
                    if content.type == "text":
                        data = json.loads(content.text)
                        print("-" * 40)
                        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                        print("-" * 40)

    except Exception as e:
        print(f"❌ [异常] {e}")

if __name__ == "__main__":
    asyncio.run(run_standard_test())