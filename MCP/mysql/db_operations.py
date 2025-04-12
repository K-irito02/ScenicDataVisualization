import json
import sys
import os
import pymysql
from pymysql.cursors import DictCursor
from tabulate import tabulate

# 读取配置文件
config_path = os.path.join(os.path.dirname(__file__), 'HieTic_and_SceAr.json')
with open(config_path, 'r') as f:
    config = json.load(f)

def create_connection(db_name):
    """创建数据库连接"""
    connection_info = next((conn for conn in config['connections'] if conn['name'] == db_name), None)
    
    if not connection_info:
        print(f'找不到数据库 "{db_name}" 的配置信息')
        return None
    
    try:
        connection = pymysql.connect(
            host=connection_info['host'],
            port=connection_info['port'],
            user=connection_info['user'],
            password=connection_info['password'],
            database=connection_info['database'],
            cursorclass=DictCursor
        )
        print(f'成功连接到 {db_name} 数据库')
        return connection
    except Exception as e:
        print(f'连接到 {db_name} 数据库时出错: {e}')
        return None

def show_tables(db_name):
    """功能1: 查看数据库中的所有表"""
    connection = create_connection(db_name)
    if not connection:
        return
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('SHOW TABLES')
            tables = cursor.fetchall()
            
            print(f'{db_name} 数据库中的表:')
            for i, table in enumerate(tables, 1):
                # 表名是字典的第一个值
                table_name = list(table.values())[0]
                print(f'{i}. {table_name}')
            
            return tables
    except Exception as e:
        print(f'查询表时出错: {e}')
    finally:
        connection.close()

def describe_table(db_name, table_name):
    """功能2: 查看指定表的结构"""
    connection = create_connection(db_name)
    if not connection:
        return
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'DESCRIBE {table_name}')
            structure = cursor.fetchall()
            
            print(f'表 {table_name} 的结构:')
            if structure:
                headers = structure[0].keys()
                table_data = [[row[col] for col in headers] for row in structure]
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
            
            return structure
    except Exception as e:
        print(f'查询表 {table_name} 结构时出错: {e}')
    finally:
        connection.close()

def query_table(db_name, table_name, limit=10):
    """功能3: 查看指定表的数据"""
    connection = create_connection(db_name)
    if not connection:
        return
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {table_name} LIMIT {limit}')
            rows = cursor.fetchall()
            
            print(f'表 {table_name} 的数据 (限制 {limit} 条):')
            if rows:
                headers = rows[0].keys()
                table_data = [[row[col] for col in headers] for row in rows]
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
            else:
                print("表中没有数据")
            
            return rows
    except Exception as e:
        print(f'查询表 {table_name} 数据时出错: {e}')
    finally:
        connection.close()

def print_usage():
    """打印使用说明"""
    print('用法:')
    print('python db_operations.py show-tables <数据库名>')
    print('python db_operations.py describe-table <数据库名> <表名>')
    print('python db_operations.py query-table <数据库名> <表名> [限制数量]')

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print_usage()
        return
    
    command = sys.argv[1]
    db_name = sys.argv[2]
    
    if command == 'show-tables':
        show_tables(db_name)
    elif command == 'describe-table':
        if len(sys.argv) < 4:
            print('需要提供表名')
            return
        table_name = sys.argv[3]
        describe_table(db_name, table_name)
    elif command == 'query-table':
        if len(sys.argv) < 4:
            print('需要提供表名')
            return
        table_name = sys.argv[3]
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        query_table(db_name, table_name, limit)
    else:
        print(f'未知命令: {command}')
        print_usage()

if __name__ == '__main__':
    main() 