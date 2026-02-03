import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

# ==========================================
# ⚙️ 配置区域 (Configuration)
# 🎯 目标：测试 Giiisp Search By ArxivNo 服务 (端口 6006)
# ==========================================
TARGET_PORT = 6006
SERVICE_NAME = "Giiisp Search By ArxivNo"
SERVER_URL = f"http://giiisp.com:{TARGET_PORT}/sse"

TEST_CASE = {
    # ⚠️ 注意：文档里这个工具名是大写开头的！
    "tool_name": "SearchByArxivNo",
    "params": {
        "key": "1706.03762",  # Attention Is All You Need 的 ID
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
                
                # 1. 验证工具名 (重点检查大小写)
                tools = await session.list_tools()
                available_tools = [t.name for t in tools.tools]
                print(f"✅ 连接成功 | 发现工具: {available_tools}")
                
                target = TEST_CASE["tool_name"]
                if target not in available_tools:
                    print(f"❌ [名称不匹配] 文档说叫 '{target}'，但实际只有: {available_tools}")
                    # 尝试自动纠错逻辑：如果列表里有唯一的工具，可能是大小写写错了
                    return

                # 2. 执行
                print(f"🔍 正在按 ID 搜索: {TEST_CASE['params']['key']} ...")
                result = await session.call_tool(name=target, arguments=TEST_CASE["params"])
                
                # 3. 解析
                for content in result.content:
                    if content.type == "text":
                        data = json.loads(content.text)
                        print("-" * 40)
                        # 看看能不能搜出 Transformer 的标题
                        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                        print("-" * 40)

    except Exception as e:
        print(f"❌ [异常] {e}")

if __name__ == "__main__":
    asyncio.run(run_standard_test())