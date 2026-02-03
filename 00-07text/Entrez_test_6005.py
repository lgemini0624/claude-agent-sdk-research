import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

# ==========================================
# ⚙️ 配置区域 (Configuration)
# 🎯 目标：测试 Entrez (NCBI) 服务 (端口 6005)
# ==========================================
TARGET_PORT = 6005
SERVICE_NAME = "Entrez (NCBI)"
SERVER_URL = f"http://giiisp.com:{TARGET_PORT}/sse"

TEST_CASE = {
    # 文档指定工具: ESearch
    "tool_name": "ESearch",
    # ⚠️ 注意：这里有两个必填参数！
    "params": {
        "db": "pubmed",   # 指定搜 PubMed 库
        "term": "covid",  # 搜新冠相关
        "retmax": 2       # 只看2条
    }
}
# ==========================================

async def run_standard_test() -> bool:
    print(f"🚀 [启动测试] 服务: {SERVICE_NAME} | 端口: {TARGET_PORT}")
    print(f"🔌 连接地址: {SERVER_URL}")

    try:
        async with sse_client(SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 1. 发现工具
                tools = await session.list_tools()
                available_tools = [t.name for t in tools.tools]
                print(f"✅ 连接成功 | 发现工具: {available_tools}")
                
                target_tool = TEST_CASE["tool_name"]
                if target_tool not in available_tools:
                    print(f"❌ [致命错误] 工具 '{target_tool}' 未找到！")
                    print(f"📋 实际可用: {available_tools}")
                    return False

                # 2. 执行调用
                print(f"🔍 [执行调用] 工具: {target_tool} | 参数: {TEST_CASE['params']}")
                result = await session.call_tool(name=target_tool, arguments=TEST_CASE['params'])
                
                # 3. 结果解析
                for content in result.content:
                    if content.type == "text":
                        print(f"\n📦 [原始响应] 长度: {len(content.text)} 字符")
                        try:
                            data = json.loads(content.text)
                            print("-" * 40)
                            # Entrez 返回的通常是 ID 列表，我们看看长啥样
                            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
                            print("-" * 40)
                        except:
                            print(content.text[:200])
                return True

    except Exception as e:
        print(f"\n❌ [异常] {e}")
        return False

if __name__ == "__main__":
    asyncio.run(run_standard_test())