from mcp.server.fastmcp import FastMCP
import pymysql
import json

# 初始化MCP服务
mcp = FastMCP("MySQL MCP")

# 数据库连接函数
def get_connection():
    """创建并返回MySQL数据库连接"""
    try:
        return pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="3143285505",
            database="scenic_area"
        )
    except Exception as e:
        print(f"数据库连接失败: {e}")
        raise e

@mcp.tool()
def list_tables() -> list:
    """列出所有数据库表"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tables

@mcp.tool()
def describe_table(table_name: str) -> list:
    """查看指定表的结构"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()
    result = []
    for column in columns:
        result.append({
            "Field": column[0],
            "Type": column[1],
            "Null": column[2],
            "Key": column[3],
            "Default": column[4],
            "Extra": column[5]
        })
    cursor.close()
    conn.close()
    return result

@mcp.tool()
def query_data(sql: str, limit: int = 1000) -> list:
    """执行SQL查询(仅支持SELECT操作)"""
    # 检查是否是SELECT查询
    if not sql.strip().upper().startswith("SELECT"):
        return {"error": "仅支持SELECT查询"}
    
    # 添加LIMIT子句以防止返回过多数据
    if "LIMIT" not in sql.upper():
        sql = f"{sql} LIMIT {limit}"
    
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        return list(results)
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()

@mcp.tool()
def get_table_count(table_name: str) -> dict:
    """获取表中的记录数量"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return {"table": table_name, "count": count}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()

@mcp.tool()
def get_table_schema(table_name: str) -> dict:
    """获取表的详细结构信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 获取列信息
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        column_info = []
        for column in columns:
            column_info.append({
                "name": column[0],
                "type": column[1],
                "nullable": column[2] == "YES",
                "key": column[3],
                "default": column[4],
                "extra": column[5]
            })
        
        # 获取索引信息
        cursor.execute(f"SHOW INDEX FROM {table_name}")
        indexes = cursor.fetchall()
        index_info = {}
        for idx in indexes:
            index_name = idx[2]  # Key_name
            if index_name not in index_info:
                index_info[index_name] = {
                    "name": index_name,
                    "unique": not bool(idx[1]),  # Non_unique
                    "columns": []
                }
            index_info[index_name]["columns"].append({
                "name": idx[4],  # Column_name
                "order": idx[6]  # Sub_part
            })
        
        return {
            "table_name": table_name,
            "columns": column_info,
            "indexes": list(index_info.values())
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()

@mcp.tool()
def get_table_sample(table_name: str, limit: int = 10) -> list:
    """获取表的数据样例"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        return list(cursor.fetchall())
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()

@mcp.tool()
def execute_query(sql: str) -> dict:
    """执行复杂SQL查询(仅读操作)，支持多表联查"""
    # 将SQL转换为小写以便检查
    sql_lower = sql.lower()
    
    # 检查是否包含写操作关键词
    write_operations = ["insert", "update", "delete", "drop", "alter", "create"]
    for op in write_operations:
        if op in sql_lower and f"'{op}'" not in sql_lower and f'"{op}"' not in sql_lower:
            return {"error": f"不支持 {op.upper()} 操作，仅允许读操作"}
    
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        start_time = time.time()
        cursor.execute(sql)
        execution_time = time.time() - start_time
        
        if cursor.description:  # 查询返回结果集
            results = list(cursor.fetchall())
            return {
                "status": "success",
                "result_count": len(results),
                "execution_time_ms": round(execution_time * 1000, 2),
                "results": results
            }
        else:  # 查询未返回结果集
            return {
                "status": "success",
                "affected_rows": cursor.rowcount,
                "execution_time_ms": round(execution_time * 1000, 2)
            }
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()

# 主程序启动
if __name__ == "__main__":
    import time
    print("MySQL MCP 服务启动中...")
    mcp.run()