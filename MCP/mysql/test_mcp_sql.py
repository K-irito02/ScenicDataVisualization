import json
from mcp.client.session import ClientSession
from mcp import stdio_client, StdioServerParameters

# Smithery MCP客户端 - 简单SQL执行示例
def main():
    try:
        # 创建连接参数
        print("准备连接到MCP服务器...")
        server_params = StdioServerParameters(
            name="测试SQL客户端",
            version="1.0.0"
        )
        
        # 使用异步方式连接
        import asyncio
        asyncio.run(run_mcp_client(server_params))
        
    except Exception as e:
        print(f"错误: {str(e)}")

async def run_mcp_client(server_params):
    print("连接到MCP服务器...")
    async with stdio_client("https://server.smithery.ai/mysql-mcp-server") as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            print("连接成功")
            
            # 列出可用工具
            tools = await session.list_tools()
            print("可用工具:")
            for tool in tools:
                print(f"- {tool.name}")
            
            # 执行简单SQL查询
            query = "SHOW DATABASES;"
            print(f"\n执行SQL: {query}")
            
            result = await session.call_tool("execute_sql", {"query": query})
            
            print("\n查询结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 