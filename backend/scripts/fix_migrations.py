"""
简单脚本，直接执行SQL修复迁移问题
"""
import os
import sys
import mysql.connector
from datetime import datetime

def fix_migrations():
    try:
        # 从环境变量或设置文件中获取数据库连接信息
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '3143285505',  # 从settings.py中获取的密码
            'database': 'scenic_area'  # 从settings.py中获取的数据库名
        }
        
        # 连接到数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 删除有问题的迁移记录(如果存在)
        cursor.execute(
            "DELETE FROM django_migrations WHERE app = 'scenic_data' AND name = '0006_remove_culturalreliclevelprice_id_and_more'"
        )
        
        # 添加新的修复迁移记录(如果不存在)
        cursor.execute(
            "SELECT COUNT(*) FROM django_migrations WHERE app = 'scenic_data' AND name = '0006_fix_missing_id'"
        )
        count = cursor.fetchone()[0]
        
        if count == 0:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                ('scenic_data', '0006_fix_missing_id', now)
            )
            print("已添加新的修复迁移记录")
        else:
            print("修复迁移记录已存在")
        
        # 提交事务并关闭连接
        conn.commit()
        cursor.close()
        conn.close()
        
        print("迁移修复成功")
        return True
    except Exception as e:
        print(f"迁移修复失败: {e}")
        return False

if __name__ == "__main__":
    print("开始修复迁移问题...")
    if fix_migrations():
        print("\n完成! 现在您可以尝试运行:")
        print("python manage.py migrate")
    else:
        print("\n修复失败，请检查数据库配置和连接")
        sys.exit(1) 