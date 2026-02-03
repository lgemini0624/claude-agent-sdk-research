import json
import asyncio
from typing import Optional, Dict, Any, List, Union
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

class GiiispMCPClient:
    """
    Giiisp MCP 服务通用客户端 SDK
    作用：封装底层连接逻辑，让上层业务（Agent）不需要关心 SSE 和 JSON 解析
    """
    
    def __init__(self, port: int, service_name: str = "Unknown"):
        self.port = port
        self.service_name = service_name
        self.base_url = f"http://giiisp.com:{port}/sse"
    
    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Optional[Union[Dict, List, str]]:
        """
        连接服务并调用指定工具
        :param tool_name: 工具名称 (如 'DeepResearch', 'search_works')
        :param args: 参数字典 (如 {'query': 'AI'})
        :return: 解析后的数据 (字典、列表或原始文本)
        """
        # 日志加个 emoji，调试心情好
        print(f"\n🔌 [{self.service_name}] 正在连接: {self.base_url} ...")
        
        try:
            # 建立 SSE 长连接
            async with sse_client(self.base_url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # 1. 验证工具是否存在 (防御性编程)
                    tools = await session.list_tools()
                    available_tools = [t.name for t in tools.tools]
                    
                    if tool_name not in available_tools:
                        print(f"❌ [SDK错误] 工具 '{tool_name}' 不存在！")
                        print(f"📋 该服务可用工具: {available_tools}")
                        return None

                    # 2. 执行调用
                    print(f"🔍 [SDK调用] {tool_name} | 参数: {args}")
                    result = await session.call_tool(name=tool_name, arguments=args)
                    
                    # 3. 统一结果解析逻辑
                    # 我们遍历返回的内容，尝试提取最有用的信息
                    final_data = []
                    for content in result.content:
                        if content.type == "text":
                            try:
                                # 尝试解析 JSON
                                data = json.loads(content.text)
                                final_data.append(data)
                            except json.JSONDecodeError:
                                # 解析不了就返回原始文本
                                final_data.append(content.text)
                    
                    # 如果结果是空的
                    if not final_data:
                        print("⚠️ [SDK警告] 调用成功但没有返回任何数据")
                        return None

                    # 如果只有一条数据，直接返回该数据；否则返回列表
                    return final_data[0] if len(final_data) == 1 else final_data

        except Exception as e:
            print(f"❌ [SDK异常] 连接 {self.service_name} 失败: {str(e)}")
            return None