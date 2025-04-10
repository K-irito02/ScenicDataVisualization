#!/usr/bin/env python
"""
测试多个景区的交通数据，帮助诊断交通数据显示问题
"""
import json
import sys
import os
import requests
from pprint import pprint

# 配置
API_BASE_URL = "http://localhost:8000/api"  # 替换为实际的API基础URL
MAX_SCENIC_ID = 20  # 测试前20个景区

def test_scenic_traffic_data(scenic_id):
    """测试指定景区ID的交通数据"""
    print(f"\n[ID: {scenic_id}] 测试景区交通数据")
    
    # 构建API URL
    url = f"{API_BASE_URL}/scenic/{scenic_id}/"
    
    try:
        # 发送GET请求
        response = requests.get(url)
        response.raise_for_status()  # 抛出HTTP错误
        
        # 解析响应数据
        data = response.json()
        
        # 基本信息
        name = data.get('name', '未知')
        print(f"景区名称: {name}")
        
        # 交通信息
        transportation = data.get('transportation', None)
        traffic_info = data.get('traffic_info', None)
        transport_mode = data.get('transport_mode', None)
        
        # 分析交通数据情况
        has_transportation = bool(transportation)
        has_traffic_info = bool(traffic_info)
        has_transport_mode = bool(transport_mode)
        
        # 打印交通数据状态
        print(f"交通数据状态:")
        print(f"  - transportation: {'有数据 ✓' if has_transportation else '无数据 ✗'}")
        print(f"  - traffic_info: {'有数据 ✓' if has_traffic_info else '无数据 ✗'}")
        print(f"  - transport_mode: {'有数据 ✓' if has_transport_mode else '无数据 ✗'}")
        
        # 判断前端是否会显示交通数据
        will_display = has_transportation or has_traffic_info
        print(f"前端显示预测: {'将显示交通数据 ✓' if will_display else '不会显示交通数据 ✗'}")
        
        # 如果有交通数据，显示数据预览
        if has_transportation or has_traffic_info:
            print("\n交通数据预览:")
            if has_transportation:
                preview = transportation[:100] + "..." if len(transportation) > 100 else transportation
                print(f"transportation: {preview}")
            if has_traffic_info and traffic_info != transportation:
                preview = traffic_info[:100] + "..." if len(traffic_info) > 100 else traffic_info
                print(f"traffic_info: {preview}")
        
        return {
            'id': scenic_id,
            'name': name,
            'has_transportation': has_transportation,
            'has_traffic_info': has_traffic_info,
            'will_display': will_display
        }
            
    except requests.exceptions.RequestException as e:
        print(f"请求错误 (ID: {scenic_id}): {e}")
        return None
    except json.JSONDecodeError:
        print(f"响应不是有效的JSON格式 (ID: {scenic_id})")
        return None
    except Exception as e:
        print(f"其他错误 (ID: {scenic_id}): {e}")
        return None

def test_multiple_scenic_spots(max_id=MAX_SCENIC_ID):
    """测试多个景点的交通数据"""
    print("=" * 60)
    print(f"测试多个景区的交通数据 (ID: 1-{max_id})")
    print("=" * 60)
    
    results = []
    
    for scenic_id in range(1, max_id + 1):
        result = test_scenic_traffic_data(scenic_id)
        if result:
            results.append(result)
    
    # 统计结果
    total = len(results)
    with_data = sum(1 for r in results if r['will_display'])
    without_data = total - with_data
    
    # 打印统计摘要
    print("\n" + "=" * 60)
    print(f"测试结果摘要:")
    print(f"总共测试景区数: {total}")
    print(f"有交通数据景区数: {with_data} ({with_data/total*100:.1f}%)")
    print(f"无交通数据景区数: {without_data} ({without_data/total*100:.1f}%)")
    print("=" * 60)
    
    # 打印无交通数据的景区列表
    if without_data > 0:
        print("\n无交通数据的景区列表:")
        for r in results:
            if not r['will_display']:
                print(f"ID: {r['id']}, 名称: {r['name']}")

if __name__ == "__main__":
    max_id = MAX_SCENIC_ID
    
    # 如果有命令行参数，使用第一个参数作为最大ID
    if len(sys.argv) > 1:
        try:
            max_id = int(sys.argv[1])
        except ValueError:
            print(f"无效的最大ID: {sys.argv[1]}, 使用默认值: {MAX_SCENIC_ID}")
    
    test_multiple_scenic_spots(max_id) 