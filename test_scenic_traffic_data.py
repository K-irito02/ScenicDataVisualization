#!/usr/bin/env python
"""
测试景区详情API提供的交通数据格式，并验证前端正确接收
"""
import json
import sys
import os
import requests
from pprint import pprint

# 设置Django环境（可选，如果需要直接访问数据库）
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
# django.setup()
# from scenic_data.models import ScenicData

# 配置
API_BASE_URL = "http://localhost:8000/api"  # 替换为实际的API基础URL
SCENIC_ID = "1"  # 替换为一个有效的景区ID

def test_scenic_detail_api():
    """测试景区详情API，检查交通数据的格式"""
    print(f"测试景区详情API (ID: {SCENIC_ID})")
    
    # 构建API URL
    url = f"{API_BASE_URL}/scenic/{SCENIC_ID}/"
    print(f"请求URL: {url}")
    
    try:
        # 发送GET请求
        response = requests.get(url)
        response.raise_for_status()  # 抛出HTTP错误
        
        # 解析响应数据
        data = response.json()
        
        # 打印基本信息
        print("\n基本信息:")
        print(f"景区名称: {data.get('name', '未知')}")
        print(f"景区ID: {data.get('scenic_id', '未知')}")
        
        # 检查并打印交通信息
        print("\n交通信息:")
        
        # 查看原始交通数据字段
        transportation = data.get('transportation', None)
        print(f"原始交通数据 (transportation): {transportation}")
        
        # 查看交通方式字段
        transport_mode = data.get('transport_mode', None)
        print(f"交通方式 (transport_mode): {transport_mode}")
        
        # 检查序列化后的交通信息
        traffic_info = data.get('trafficInfo', [])
        print("\n序列化后的交通信息 (trafficInfo):")
        if traffic_info:
            for i, info in enumerate(traffic_info, 1):
                print(f"交通信息 #{i}:")
                print(f"  类型: {info.get('type', '未知')}")
                print(f"  类型名称: {info.get('typeName', '未知')}")
                print(f"  描述: {info.get('description', '无')}")
        else:
            print("无交通信息数据")
            
        # 提供改进建议
        print("\n改进建议:")
        if not transportation and not traffic_info:
            print("数据库中可能没有交通信息数据，建议检查数据是否正确导入")
        
        if traffic_info:
            print("前端应处理的交通信息格式:")
            print("""
// 前端代码中处理交通信息的示例:
scenic.value = {
  // 其他属性...
  
  // 直接使用后端的原始交通数据，不按类型分类
  trafficInfo: data.traffic_info ? [{description: data.traffic_info}] : [],
}
""")
        else:
            print("需要添加原始交通数据")
            print("""
// 序列化器中需要添加:
class ScenicDetailSerializer(serializers.ModelSerializer):
    # 其他字段...
    traffic_info = serializers.CharField(source='transportation')
    
    class Meta:
        model = ScenicData
        fields = (..., 'traffic_info', ...)
""")
                
        return True
            
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return False
    except json.JSONDecodeError:
        print("响应不是有效的JSON格式")
        return False
    except Exception as e:
        print(f"其他错误: {e}")
        return False

def test_frontend_data_processing():
    """测试前端处理后端交通数据的代码片段"""
    print("\n测试前端数据处理")
    
    # 模拟后端返回的数据
    mock_backend_data = {
        "scenic_id": "1",
        "name": "测试景区",
        "transportation": "乘坐公交车在XX站下车，步行10分钟可到达景区。自驾车可直接导航到景区停车场。",
        "transport_mode": "公交,自驾",
        "trafficInfo": [
            {
                "type": "公交",
                "typeName": "公共汽车",
                "description": "乘坐公交车在XX站下车，步行10分钟可到达景区。自驾车可直接导航到景区停车场。"
            },
            {
                "type": "自驾",
                "typeName": "自驾车",
                "description": "乘坐公交车在XX站下车，步行10分钟可到达景区。自驾车可直接导航到景区停车场。"
            }
        ],
        # 其他数据...
    }
    
    # 模拟当前前端处理方式
    current_frontend_processing = """
    scenic.value = {
      // 其他属性...
      trafficInfo: data.trafficInfo || [],
    }
    """
    
    # 模拟新的前端处理方式
    new_frontend_processing = """
    scenic.value = {
      // 其他属性...
      trafficInfo: data.transportation ? [{description: data.transportation}] : [],
    }
    """
    
    print("当前前端处理方式:")
    print(current_frontend_processing)
    
    print("\n建议的前端处理方式:")
    print(new_frontend_processing)
    
    print("\n这样处理后，前端将直接显示原始交通数据，不再按交通类型分类显示")


if __name__ == "__main__":
    print("=" * 50)
    print("景区交通数据测试")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        SCENIC_ID = sys.argv[1]
        
    test_scenic_detail_api()
    test_frontend_data_processing() 