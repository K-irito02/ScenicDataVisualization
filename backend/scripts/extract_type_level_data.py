#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取景区类型和级别数据并以JSON格式输出
这个脚本用于生成前端搜索功能需要的类型和级别数据
"""

import os
import sys
import json
import re
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

def extract_type_level_data():
    """
    从数据库中提取景区类型和级别数据
    返回结构化的类型和级别数据
    """
    # 获取所有景区数据
    scenic_data = ScenicData.objects.all()
    
    # 初始化数据结构
    type_level_data = {
        "types": set(),  # 景区类型集合
        "levels": set()  # 景区级别集合
    }
    
    # 遍历景区数据，提取并组织类型和级别信息
    for scenic in scenic_data:
        if not scenic.scenic_type:
            continue
            
        # 分割类型字段
        items = scenic.scenic_type.split(',')
        
        for item in items:
            item = item.strip()
            if not item:
                continue
                
            # 处理包含冒号的情况（如"国家级:4A"）
            if ':' in item:
                try:
                    type_part, level_part = item.split(':', 1)
                    if type_part.strip():
                        type_level_data["types"].add(type_part.strip())
                    if level_part.strip():
                        type_level_data["levels"].add(level_part.strip())
                except Exception:
                    # 解析失败时直接添加整个项
                    type_level_data["types"].add(item)
            # 处理含A景区的情况
            elif 'A景区' in item or re.search(r'[1-5]A', item):
                type_level_data["levels"].add(item)
            # 其他情况视为类型
            else:
                type_level_data["types"].add(item)
    
    # 转换集合为排序后的列表
    result = {
        "types": sorted(list(type_level_data["types"])),
        "levels": sorted(list(type_level_data["levels"]))
    }
    
    return result

def main():
    """
    主函数，提取数据并输出为JSON文件
    """
    print("开始提取景区类型和级别数据...")
    type_level_data = extract_type_level_data()
    
    # 输出为JSON文件
    with open('type_level_data.json', 'w', encoding='utf-8') as f:
        json.dump(type_level_data, f, ensure_ascii=False, indent=2)
    
    # 打印统计信息
    types_count = len(type_level_data["types"])
    levels_count = len(type_level_data["levels"])
    
    print(f"数据提取完成！共有{types_count}个类型，{levels_count}个级别")
    print(f"数据已保存到 type_level_data.json")
    
    # 打印前端代码集成提示
    print("\n将以下数据粘贴到前端代码(Search.vue)中:")
    print("const typeLevelData = " + json.dumps(type_level_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 