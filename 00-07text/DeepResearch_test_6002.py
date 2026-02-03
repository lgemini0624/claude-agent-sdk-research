import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

# ==========================================
# ⚙️ 配置区域 (Configuration)
# 🎯 目标：测试 DeepResearch 服务 (端口 6002)
# ==========================================
TARGET_PORT = 6002
SERVICE_NAME = "DeepResearch (Giiisp)"
SERVER_URL = f"http://giiisp.com:{TARGET_PORT}/sse"

TEST_CASE = {
    # 📚 工具名: DeepResearch
    "tool_name": "DeepResearch",
    "params": {
        "searchQuery": "AI Education",
        "count": 2
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
                    return False

                # 2. 执行调用
                print(f"🔍 [执行调用] 工具: {target_tool} | 参数: {TEST_CASE['params']}")
                result = await session.call_tool(name=target_tool, arguments=TEST_CASE['params'])
                
                # 3. 结果解析
                for content in result.content:
                    if content.type == "text":
                        print(f"\n📦 [原始响应] 长度: {len(content.text)} 字符")
                        try:
                            response_data = json.loads(content.text)
                            
                            # === 🚑 DeepResearch 专属解析逻辑 (保留原汁原味) ===
                            # 1. 剥第一层
                            outer_data = response_data.get('data', {})
                            
                            # 2. 剥第二层 (核心修复逻辑)
                            papers_list = []
                            if isinstance(outer_data, dict):
                                papers_list = outer_data.get('data', [])
                            elif isinstance(outer_data, list):
                                papers_list = outer_data
                            # ================================================

                            print("-" * 40)
                            if papers_list:
                                print(f"🎉 成功提取到 {len(papers_list)} 篇论文：")
                                for i, paper in enumerate(papers_list):
                                    # 确保是字典
                                    if not isinstance(paper, dict): continue
                                    
                                    title = paper.get('title') or "未知标题"
                                    doi = paper.get('doi') or "无链接"
                                    # 打印漂亮的信息
                                    print(f"  {i+1}. [{doi}] {title}")
                            else:
                                print("⚠️ 未提取到论文列表，打印原始数据前 500 字：")
                                print(json.dumps(response_data, indent=2, ensure_ascii=False)[:500])
                            print("-" * 40)

                        except:
                            print(content.text[:500])
                return True

    except Exception as e:
        print(f"\n❌ [异常] {e}")
        return False

if __name__ == "__main__":
    asyncio.run(run_standard_test())