import os
import json
import asyncio
from mcp.client.session import ClientSession
from mcp import stdio_client

async def connect_to_mcp_server():
    """连接到Smithery的MySQL MCP服务器"""
    try:
        # 使用异步方式连接到MCP服务器
        print("正在连接到MCP服务器...")
        async with stdio_client("https://server.smithery.ai/mysql-mcp-server") as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化连接
                await session.initialize()
                print("成功连接到MCP服务器")
                
                # 获取并显示可用工具
                tools = await session.list_tools()
                print(f"可用工具: {', '.join([t.name for t in tools])}")
                
                # 执行查询
                await execute_queries(session)
    except Exception as e:
        print(f"连接MCP服务器失败: {str(e)}")

async def execute_queries(session):
    """执行SQL查询"""
    try:
        # 示例查询 - 获取景区数据
        print("\n执行查询示例:")
        query = "SELECT * FROM scenic_area LIMIT 10;"
        print(f"SQL: {query}")
        
        result = await session.call_tool("execute_sql", {"query": query})
        
        if result:
            print("\n查询结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 示例2 - 查询hierarchy_ticketanalysis数据库
        print("\n示例2 - 查询hierarchy_ticketanalysis数据库")
        print("注意: 您需要先在Smithery平台上将mysqlDatabase配置更改为'hierarchy_ticketanalysis'")
        query2 = "SELECT * FROM hierarchy_ticketanalysis LIMIT 10;"
        print(f"SQL: {query2}")
        
        # 在实际应用中，您需要先修改Smithery平台上的配置，然后再进行查询
        # result2 = await session.call_tool("execute_sql", {"query": query2})
        # if result2:
        #     print("\n查询结果:")
        #     print(json.dumps(result2, ensure_ascii=False, indent=2))
        
        print("\n完成所有查询")
    except Exception as e:
        print(f"执行SQL查询失败: {str(e)}")

def setup_mysql_config():
    """设置MySQL配置"""
    # 在实际应用中，您可能需要从配置文件或环境变量中读取这些信息
    config = {
        "mysqlHost": "localhost",  # 本地MySQL主机地址
        "mysqlPort": 3306,         # MySQL默认端口
        "mysqlUser": "root",       # 您的MySQL用户名
        "mysqlPassword": "",       # 您的MySQL密码
        "mysqlDatabase": "scenic_area"  # 您要连接的数据库名称
    }
    
    print("MySQL连接配置:")
    for key, value in config.items():
        if key != "mysqlPassword":
            print(f"- {key}: {value}")
        else:
            print(f"- {key}: ******")
    
    # 在实际应用中，您需要将这些配置提交到Smithery平台
    print("\n注意: 您需要将这些配置提交到Smithery平台")
    print("请访问 https://smithery.ai/server/mysql-mcp-server 并在配置页面输入这些信息")
    
    return config

def main():
    # 设置MySQL配置
    config = setup_mysql_config()
    
    # 运行异步函数
    asyncio.run(connect_to_mcp_server())

if __name__ == "__main__":
    main()
