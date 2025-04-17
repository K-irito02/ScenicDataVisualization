import requests
import json
import sys
import os
import django
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

def check_scenic_table():
    """检查景区数据表内容"""
    print("\n=== 检查景区数据表 ===")
    
    try:
        with connections['default'].cursor() as cursor:
            # 检查景区表
            cursor.execute("SHOW TABLES LIKE 'scenic_spots'")
            if cursor.fetchone():
                print("发现景区表: scenic_spots")
                
                # 查看表结构
                cursor.execute("DESCRIBE scenic_spots")
                columns = cursor.fetchall()
                print("\n表结构:")
                for column in columns:
                    print(f"  {column[0]} - {column[1]}")
                
                # 查看记录数
                cursor.execute("SELECT COUNT(*) FROM scenic_spots")
                count = cursor.fetchone()[0]
                print(f"\n景区总数: {count}")
                
                # 查看前5条记录
                if count > 0:
                    cursor.execute("SELECT * FROM scenic_spots LIMIT 5")
                    records = cursor.fetchall()
                    print("\n前5条景区记录:")
                    for i, record in enumerate(records):
                        print(f"\n记录 {i+1}:")
                        for j, column in enumerate(columns):
                            print(f"  {column[0]}: {record[j]}")
                
                # 返回第一条记录的ID作为可用ID
                cursor.execute("SELECT id FROM scenic_spots LIMIT 1")
                first_id = cursor.fetchone()
                if first_id:
                    return str(first_id[0])
            else:
                print("未找到景区表: scenic_spots")
                
                # 尝试查找其他可能的景区相关表
                cursor.execute("SHOW TABLES LIKE '%scenic%'")
                scenic_tables = cursor.fetchall()
                if scenic_tables:
                    print("\n找到与景区相关的表:")
                    for table in scenic_tables:
                        print(f"  {table[0]}")
                else:
                    print("\n未找到任何与景区相关的表")
    except Exception as e:
        print(f"检查景区表时出错: {str(e)}")
    
    return None

# 测试景区详情API
def test_scenic_detail_api(scenic_id):
    """测试景区详情API功能"""
    
    base_url = "http://localhost:8000/api"
    endpoint = f"/scenic/{scenic_id}/"
    
    print(f"\n=== 测试景区详情API ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    print(f"请求URL: {base_url}{endpoint}")
    
    try:
        response = requests.get(f"{base_url}{endpoint}")
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"数据类型: {type(data)}")
            print(f"数据结构: {json.dumps(list(data.keys()) if isinstance(data, dict) else '非字典数据', ensure_ascii=False)}")
            print("\n景区详情数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"请求出错: {str(e)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    # 首先检查景区表，获取可用的景区ID
    available_id = check_scenic_table()
    
    # 如果提供了命令行参数，使用它作为景区ID
    # 否则使用从数据库中获取的ID，如果都没有则使用默认ID
    scenic_id = sys.argv[1] if len(sys.argv) > 1 else (available_id or "1")
    print(f"\n使用景区ID: {scenic_id}")
    
    # 测试景区详情API
    test_scenic_detail_api(scenic_id) 