import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

# ==========================================
# ⚙️ 配置区域 (Configuration)
# 🎯 目标：测试 BioC 服务 (端口 6001)
# ==========================================
TARGET_PORT = 6001
SERVICE_NAME = "BioC (PMC)"
SERVER_URL = f"http://giiisp.com:{TARGET_PORT}/sse"

TEST_CASE = {
    # 📚 根据之前的测试，线上服务包含 'get_article_info'
    # 相比 get_article 返回大量 XML，这个工具更适合做连通性测试
    "tool_name": "get_article_info",
    "params": {
        "id": "PMC8055628"  # 使用一个真实存在的 PMC 文章 ID
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
                    # 如果找不到预设工具，可以提示用户换一个试试
                    if "get_article" in available_tools:
                        print("💡 提示：检测到 'get_article' 可用，你可以修改上方的 TEST_CASE 配置来测试它。")
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
                            
                            # ✨ BioC 专属优化：如果返回的是 info 对象，打印出来
                            if isinstance(data, dict):
                                if "success" in data and data.get("success") is True:
                                    print("🎉 获取成功！文章信息如下：")
                                    # 打印除去 success/status 之外的实际数据
                                    clean_data = {k: v for k, v in data.items() if k not in ['success', 'status']}
                                    print(json.dumps(clean_data, indent=2, ensure_ascii=False))
                                else:
                                    # 打印前 1000 个字符防止刷屏
                                    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
                            else:
                                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
                                
                            print("-" * 40)
                        except:
                            # 如果不是 JSON (比如 get_article 可能返回 XML)，直接打印文本
                            print(content.text[:500] + "...")
                return True

    except Exception as e:
        print(f"\n❌ [异常] {e}")
        return False

if __name__ == "__main__":
    asyncio.run(run_standard_test())