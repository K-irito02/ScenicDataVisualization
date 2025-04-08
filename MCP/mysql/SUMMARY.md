# Smithery MySQL MCP 总结

在尝试了多种方法后，我们发现以下是在Cursor中使用Smithery的MySQL MCP服务器的最佳实践：

## 最佳实践

1. **使用Cursor内置MCP功能** - Cursor已经内置了MCP客户端，可以直接使用`mcp__execute_sql`工具执行SQL查询：

   ```
   <function_calls>
   <invoke name="mcp__execute_sql">
   <parameter name="query">SELECT * FROM your_table LIMIT 10;</parameter>
   </invoke>
   </function_calls>
   ```

2. **在Smithery平台配置MySQL连接** - 在使用MCP前，确保已经在Smithery平台上正确配置了MySQL连接信息：
   - 访问 https://smithery.ai/server/mysql-mcp-server
   - 配置MySQL主机、端口、用户名、密码和数据库名称
   - 点击"Save and Connect"保存配置

3. **数据库切换** - 如果需要切换数据库（如从`scenic_area`切换到`hierarchy_ticketanalysis`），需要在Smithery平台上更改配置中的`mysqlDatabase`字段。

## 注意事项

1. **一次只能连接一个数据库** - MCP服务器一次只能连接到一个数据库，如果需要查询不同的数据库，需要更改配置。

2. **安全考虑** - 出于安全原因，建议为MCP连接创建一个具有有限权限的专用数据库用户，而不是使用root用户。

3. **连接问题排查** - 如果连接失败，请检查：
   - MySQL服务器是否正在运行
   - 您的连接信息（主机、端口、用户名、密码）是否正确
   - 您指定的数据库是否存在
   - MySQL用户是否有访问指定数据库的权限

4. **Cursor集成** - Cursor已经内置了与Smithery MCP服务器的集成，所以不需要手动编写复杂的连接代码。

## 高级用法

虽然不推荐，但如果您需要在自己的Python脚本中连接到MySQL MCP服务器，请查看本仓库中的示例代码：
- `scenic_area.py` - 异步连接示例
- `test_mcp_sql.py` - 简单连接测试
- `direct_api.py` - 直接API调用示例