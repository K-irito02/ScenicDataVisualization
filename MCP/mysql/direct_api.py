import requests
import json

def main():
    """使用直接API访问MySQL MCP服务器的示例"""
    try:
        # Smithery API端点 - 根据文档修正
        api_url = "https://server.smithery.ai/mysql-mcp-server"
        
        # 设置MySQL配置
        mysql_config = {
            "mysqlHost": "localhost",
            "mysqlPort": 3306,
            "mysqlUser": "root",
            "mysqlPassword": "3143285505",
            "mysqlDatabase": "scenic_area"
        }
        
        print("MySQL配置:")
        for key, value in mysql_config.items():
            if key != "mysqlPassword":
                print(f"- {key}: {value}")
            else:
                print(f"- {key}: ******")
        
        print("\n注意: 您需要在Smithery平台上配置这些连接信息")
        print("请访问 https://smithery.ai/server/mysql-mcp-server 并配置您的MySQL连接")
        
        # 测试API连接
        print("\n尝试执行SQL查询...")
        
        # 示例SQL查询
        sql_query = "SHOW DATABASES;"
        
        # 构建请求
        payload = {
            "query": sql_query
        }
        
        # 发送请求
        response = requests.post(
            f"{api_url}/execute_sql", 
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            print("\n查询结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"API请求失败。状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            print("\n您可能需要先在Smithery平台上配置您的MySQL连接信息，或者检查API路径是否正确。")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main() 