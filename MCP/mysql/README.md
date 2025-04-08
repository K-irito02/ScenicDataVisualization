# MySQL MCP 客户端

这是一个使用Smithery的MySQL MCP服务器连接到MySQL数据库的示例代码。

## 安装依赖

首先，安装必要的包:

```bash
pip install mcp smithery
```

## 配置MySQL连接

在使用这些脚本之前，您需要在Smithery平台上配置您的MySQL连接信息:

1. 访问 [https://smithery.ai/server/mysql-mcp-server](https://smithery.ai/server/mysql-mcp-server)
2. 登录您的Smithery账户
3. 在配置页面输入以下信息:
   - mysqlHost: 您的MySQL主机地址(通常是localhost或127.0.0.1)
   - mysqlPort: MySQL端口(默认是3306)
   - mysqlUser: 您的MySQL用户名
   - mysqlPassword: 您的MySQL密码
   - mysqlDatabase: 您要连接的数据库名称
4. 点击"Save and Connect"保存配置

## 脚本说明

### scenic_area.py

这个脚本展示了如何连接到scenic_area数据库并执行查询。它还包含了如何连接到hierarchy_ticketanalysis数据库的示例代码(需要先修改Smithery平台上的配置)。

运行方法:

```bash
python scenic_area.py
```

### test_mcp_sql.py

这是一个简单的测试脚本，用于执行基本的SQL查询(如SHOW DATABASES)并验证连接是否正常工作。

运行方法:

```bash
python test_mcp_sql.py
```

## 注意事项

1. 每次只能连接到一个数据库。如果需要切换数据库，需要在Smithery平台上修改配置。
2. 确保您的MySQL服务器允许外部连接(如果需要从非本地环境访问)。
3. 为了安全起见，建议为连接创建一个具有有限权限的专用数据库用户，而不是使用root用户。

## 推荐使用方法

### 在Cursor中直接使用MCP (推荐)

Cursor已经内置了对Smithery MCP服务器的支持，这是最简单的使用方法:

1. 确保已经在Smithery平台上配置了您的MySQL连接
2. 在Cursor中，您可以直接使用`mcp__execute_sql`工具执行查询:

```
<function_calls>
<invoke name="mcp__execute_sql">
<parameter name="query">SELECT * FROM your_table LIMIT 10;