#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
将生成的位置数据和类型级别数据更新到前端代码中
这个脚本会自动修改前端的搜索页面代码
"""

import os
import sys
import json
import re
import subprocess

# 脚本路径
LOCATION_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extract_location_data.py')
TYPE_LEVEL_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extract_type_level_data.py')

# 前端代码路径
FRONTEND_SEARCH_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                   'forward', 'my-forward', 'src', 'views', 'dashboard', 'Search.vue')

def run_extraction_scripts():
    """
    运行数据提取脚本，获取位置数据和类型级别数据
    """
    print("正在提取位置数据...")
    subprocess.run([sys.executable, LOCATION_SCRIPT], check=True)
    
    print("\n正在提取类型和级别数据...")
    subprocess.run([sys.executable, TYPE_LEVEL_SCRIPT], check=True)
    
    # 读取生成的JSON文件
    with open('location_data.json', 'r', encoding='utf-8') as f:
        location_data = json.load(f)
    
    with open('type_level_data.json', 'r', encoding='utf-8') as f:
        type_level_data = json.load(f)
    
    return location_data, type_level_data

def update_frontend_code(location_data, type_level_data):
    """
    更新前端代码中的数据
    """
    print(f"\n正在更新前端代码 {FRONTEND_SEARCH_FILE}...")
    
    # 读取前端代码
    with open(FRONTEND_SEARCH_FILE, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 提取前端代码中的脚本部分
    script_match = re.search(r'<script lang="ts">(.*?)</script>', code, re.DOTALL)
    if not script_match:
        print("错误：无法在前端代码中找到脚本部分")
        return False
    
    script_code = script_match.group(1)
    
    # 查找并替换filterOptions对象定义
    filter_options_pattern = r'const filterOptions = reactive\({[^}]*provinces:[^]]*\][^}]*cities:[^}]*\}[^}]*types:[^]]*\][^}]*levels:[^]]*\][^}]*\}?\)'
    
    # 构建新的filterOptions对象
    new_filter_options = f"""const filterOptions = reactive({{
      provinces: {json.dumps(location_data['provinces'], ensure_ascii=False)},
      cities: {json.dumps(location_data['cities'], ensure_ascii=False)},
      types: {json.dumps(type_level_data['types'], ensure_ascii=False)},
      levels: {json.dumps(type_level_data['levels'], ensure_ascii=False)}
    }})"""
    
    # 替换filterOptions对象
    if re.search(filter_options_pattern, script_code, re.DOTALL):
        new_script_code = re.sub(filter_options_pattern, new_filter_options, script_code, flags=re.DOTALL)
    else:
        print("警告：未找到filterOptions对象定义，可能需要手动更新")
        # 添加districts数据到script代码末尾
        new_script_code = script_code + f"""
    // 区县数据
    const districtData = {json.dumps(location_data['districts'], ensure_ascii=False)};
    """
    
    # 替换整个script标签内容
    new_code = code.replace(script_match.group(1), new_script_code)
    
    # 写回前端代码文件
    with open(FRONTEND_SEARCH_FILE, 'w', encoding='utf-8') as f:
        f.write(new_code)
    
    print("前端代码更新成功！")
    return True

def main():
    """
    主函数
    """
    print("开始更新前端筛选数据...")
    
    # 运行数据提取脚本
    location_data, type_level_data = run_extraction_scripts()
    
    # 更新前端代码
    success = update_frontend_code(location_data, type_level_data)
    
    if success:
        print("\n所有工作已完成！前端筛选数据已更新。")
        print("现在您可以启动前端项目查看更新后的效果了。")
    else:
        print("\n更新前端代码失败，请手动更新。")
        print(f"位置数据和类型级别数据已生成在当前目录: location_data.json 和 type_level_data.json")

if __name__ == "__main__":
    main() 