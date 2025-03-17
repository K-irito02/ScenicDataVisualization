import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

def list_all_tables():
    """列出数据库中所有表"""
    with connections['default'].cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\n数据库中的所有表:")
        for table in tables:
            print(table[0])
        return [table[0] for table in tables]

def check_table_columns(table_name):
    """检查指定表的列结构"""
    with connections['default'].cursor() as cursor:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        print(f"\n{table_name} 表的列结构:")
        for column in columns:
            print(column)

def check_table_exists(table_name):
    """检查表是否存在"""
    with connections['default'].cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE %s", [table_name])
        result = cursor.fetchone()
        return result is not None

def check_column_exists(table_name, column_name):
    """检查列是否存在于表中"""
    if not check_table_exists(table_name):
        print(f"\n表 {table_name} 不存在")
        return False
    
    with connections['default'].cursor() as cursor:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        exists = column_name in column_names
        if exists:
            print(f"\n列 {column_name} 存在于表 {table_name} 中")
        else:
            print(f"\n列 {column_name} 不存在于表 {table_name} 中")
        return exists

def check_scenic_data_tables():
    """专门检查scenic_data应用相关的表"""
    with connections['default'].cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE 'scenic_data_%'")
        tables = cursor.fetchall()
        print("\nscenic_data应用的表:")
        for table in tables:
            print(table[0])
            check_table_columns(table[0])

if __name__ == '__main__':
    # 列出所有表
    all_tables = list_all_tables()
    
    # 检查summary_table表结构
    if check_table_exists('summary_table'):
        check_table_columns('summary_table')
        # 检查city列是否存在
        check_column_exists('summary_table', 'city')
    else:
        print("\nsummary_table表不存在")
    
    # 检查scenic_data_scenicdata表
    if check_table_exists('scenic_data_scenicdata'):
        check_table_columns('scenic_data_scenicdata')
    
    # 检查scenic_data应用相关的表
    check_scenic_data_tables()
    
    # 如果要检查其他表，可以取消下面的注释并填入表名
    # 例如：check_table_columns('user_management_userprofile')
    
    # 对于特定的表，可以使用下面的代码
    print("\n您可以输入表名来查看特定表的结构（输入'q'退出）:")
    while True:
        table_input = input("请输入表名: ")
        if table_input.lower() == 'q':
            break
        if table_input in all_tables:
            check_table_columns(table_input)
        else:
            print(f"表 {table_input} 不存在") 