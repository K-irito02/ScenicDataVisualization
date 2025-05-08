#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取景区位置数据（省份、城市、区县）并以JSON格式输出
这个脚本用于生成前端搜索功能需要的位置数据
"""

import os
import sys
import json
import django

# 将当前目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# 导入数据模型
from scenic_data.models import ScenicData

def extract_location_data():
    """
    从数据库中提取省份、城市和区县数据
    返回结构化的位置数据
    """
    # 获取所有景区数据
    scenic_data = ScenicData.objects.all()
    
    # 初始化数据结构
    location_data = {
        "provinces": [],            # 所有省份列表
        "cities": {},               # 按省份组织的城市字典 {"省份": ["城市1", "城市2"]}
        "districts": {}             # 按城市组织的区县字典 {"省份_城市": ["区县1", "区县2"]}
    }
    
    # 遍历景区数据，提取并组织位置信息
    for scenic in scenic_data:
        province = scenic.province
        city = scenic.city
        district = scenic.district
        
        # 处理省份
        if province and province not in location_data["provinces"]:
            location_data["provinces"].append(province)
        
        # 处理城市
        if province and city:
            if province not in location_data["cities"]:
                location_data["cities"][province] = []
            
            if city not in location_data["cities"][province]:
                location_data["cities"][province].append(city)
        
        # 处理区县
        if province and city and district:
            city_key = f"{province}_{city}"
            if city_key not in location_data["districts"]:
                location_data["districts"][city_key] = []
            
            if district not in location_data["districts"][city_key]:
                location_data["districts"][city_key].append(district)
    
    # 对所有列表排序
    location_data["provinces"].sort()
    
    for province in location_data["cities"]:
        location_data["cities"][province].sort()
    
    for city_key in location_data["districts"]:
        location_data["districts"][city_key].sort()
    
    return location_data

def main():
    """
    主函数，提取数据并输出为JSON文件
    """
    print("开始提取景区位置数据...")
    location_data = extract_location_data()
    
    # 输出为JSON文件
    with open('location_data.json', 'w', encoding='utf-8') as f:
        json.dump(location_data, f, ensure_ascii=False, indent=2)
    
    # 打印统计信息
    provinces_count = len(location_data["provinces"])
    cities_count = sum(len(cities) for cities in location_data["cities"].values())
    districts_count = sum(len(districts) for districts in location_data["districts"].values())
    
    print(f"数据提取完成！共有{provinces_count}个省份，{cities_count}个城市，{districts_count}个区县")
    print(f"数据已保存到 location_data.json")
    
    # 打印前端代码集成提示
    print("\n将以下数据粘贴到前端代码(Search.vue)中:")
    print("const locationData = " + json.dumps(location_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 