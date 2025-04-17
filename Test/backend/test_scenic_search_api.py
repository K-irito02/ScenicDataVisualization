import requests
import json
import os
import sys
from datetime import datetime

# 测试景区搜索API
def test_scenic_search_api():
    """测试景区搜索API功能"""
    
    base_url = "http://localhost:8000/api"
    endpoint = "/scenic/search/"
    
    print(f"=== 测试景区搜索API ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 测试用例1: 无参数搜索，获取所有景区
    print("\n测试用例1: 无参数搜索，获取所有景区")
    response = requests.get(f"{base_url}{endpoint}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  状态码: {response.status_code}")
        print(f"  返回景区数量: {len(data)}")
        if len(data) > 0:
            print(f"  第一条数据: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
    else:
        print(f"  请求失败，状态码: {response.status_code}")
        print(f"  错误信息: {response.text}")
    
    # 测试用例2: 关键词搜索
    print("\n测试用例2: 关键词搜索")
    params = {"keyword": "长城"}
    response = requests.get(f"{base_url}{endpoint}", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  状态码: {response.status_code}")
        print(f"  返回景区数量: {len(data)}")
        if len(data) > 0:
            print(f"  第一条数据: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
    else:
        print(f"  请求失败，状态码: {response.status_code}")
        print(f"  错误信息: {response.text}")
    
    # 测试用例3: 筛选条件组合
    print("\n测试用例3: 筛选条件组合")
    params = {
        "province": "北京",
        "priceRange": "0,500"
    }
    response = requests.get(f"{base_url}{endpoint}", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  状态码: {response.status_code}")
        print(f"  返回景区数量: {len(data)}")
        if len(data) > 0:
            print(f"  第一条数据: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
    else:
        print(f"  请求失败，状态码: {response.status_code}")
        print(f"  错误信息: {response.text}")
    
    # 测试用例4: 测试分页参数
    print("\n测试用例4: 测试分页参数")
    params = {
        "page": 1,
        "page_size": 10
    }
    response = requests.get(f"{base_url}{endpoint}", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  状态码: {response.status_code}")
        print(f"  返回景区数量: {len(data)}")
        if len(data) > 0:
            print(f"  第一条数据: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
    else:
        print(f"  请求失败，状态码: {response.status_code}")
        print(f"  错误信息: {response.text}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_scenic_search_api() 