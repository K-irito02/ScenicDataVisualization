import requests
import json
import argparse
import os
from urllib.parse import quote

def test_district_distribution(province, city):
    """测试区县景区分布数据API"""
    url = f"http://localhost:8000/api/data/district-distribution/{quote(province)}/{quote(city)}/"
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功获取{province}{city}的区县数据:")
            print(f"总共{len(data)}个区县")
            
            # 显示前五个区县的数据
            for i, district in enumerate(data[:5]):
                print(f"{i+1}. {district['name']}: {district['value']}个景区")
                if 'scenic_spots' in district:
                    print(f"   景点数量: {len(district['scenic_spots'])}")
            
            # 保存到文件
            filename = f"{province}_{city}_district_distribution.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"完整数据已保存到: {filename}")
            
            return data
        else:
            print(f"请求失败: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"请求出错: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="测试区县景区分布API")
    parser.add_argument("--province", type=str, default="上海市", help="省份名称")
    parser.add_argument("--city", type=str, default="市辖区", help="城市名称")
    
    args = parser.parse_args()
    
    print(f"测试{args.province}{args.city}的区县分布数据...")
    test_district_distribution(args.province, args.city) 