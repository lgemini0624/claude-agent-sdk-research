import json
import asyncio
import traceback
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

# ==========================================
# ⚙️ 配置区域 (Configuration)
# 专业做法：把可能变动的参数提取到最上方
# 🎯 目标：测试 Giiisp Arxiv 服务 (端口 6003)
# ==========================================
TARGET_PORT = 6003
SERVICE_NAME = "Giiisp Arxiv"
SERVER_URL = f"http://giiisp.com:{TARGET_PORT}/sse"

# 根据文档定义的测试用例
TEST_CASE = {
    "tool_name": "searchArxivByAbstract",  # ⚠️ 文档指定的工具名
    "params": {
        "key": "Large Language Models",    # ⚠️ 文档指定的参数名
        "pageSize": 2
    }
}
# ==========================================

async def run_standard_test() -> bool:
    """
    执行标准化的 MCP 接口测试
    Returns: True if success, False if failed
    """
    print(f"🚀 [启动测试] 服务: {SERVICE_NAME} | 端口: {TARGET_PORT}")
    print(f"🔌 连接地址: {SERVER_URL}")

    try:
        async with sse_client(SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # --- 步骤 1: 验证工具列表 (Discovery) ---
                tools = await session.list_tools()
                available_tools = [t.name for t in tools.tools]
                print(f"✅ 连接成功 | 发现工具: {available_tools}")
                
                target_tool = TEST_CASE["tool_name"]
                
                # 🛡️ 防御性检查：文档里的工具真的存在吗？
                if target_tool not in available_tools:
                    print(f"❌ [致命错误] 预期工具 '{target_tool}' 未找到！")
                    print(f"💡 建议：请检查文档是否过期，或尝试使用列表中的其他工具。")
                    return False

                # --- 步骤 2: 执行调用 (Execution) ---
                print(f"🔍 [执行调用] 工具: {target_tool} | 参数: {TEST_CASE['params']}")
                
                result = await session.call_tool(
                    name=target_tool,
                    arguments=TEST_CASE["params"]
                )
                
                # --- 步骤 3: 结果验证与解析 (Validation & Parsing) ---
                if not result.content:
                    print("⚠️ [警告] 调用成功但没有返回内容。")
                    return True

                for content in result.content:
                    if content.type == "text":
                        print(f"\n📦 [原始响应] 长度: {len(content.text)} 字符")
                        
                        try:
                            # 尝试解析 JSON
                            data = json.loads(content.text)
                            
                            # 🔍 深度解析：针对 Arxiv 可能的返回结构
                            # 通常 Arxiv API 返回的可能是 data.data 或者是直接的列表
                            # 我们做一个通用的打印，方便肉眼检查
                            print("-" * 40)
                            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000]) # 只看前1000字符
                            print("-" * 40)
                            
                            # 简单的断言 (Assertion) - 类似于自动化测试
                            if isinstance(data, dict) and "success" in data and not data["success"]:
                                print("❌ [业务失败] 接口返回 success: false")
                            else:
                                print("✅ [测试通过] 数据解析正常")
                                
                        except json.JSONDecodeError:
                            print("⚠️ [格式警告] 返回的不是 JSON，打印原文:")
                            print(content.text[:200])
                
                return True

    except Exception as e:
        print(f"\n❌ [异常中断] 发生未处理的错误:")
        print(f"   {e}")
        # traceback.print_exc() # 调试时可以打开这行
        return False

if __name__ == "__main__":
    asyncio.run(run_standard_test())