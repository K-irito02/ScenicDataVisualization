import requests
import json
import time
from datetime import datetime
import sys

# 测试URL
BASE_URL = "http://localhost:8000/api"
SEARCH_ENDPOINT = "/scenic/search/"

def test_scenic_type_level_combinations():
    """测试不同景区类型和级别组合的搜索功能"""
    print(f"=== 景区类型和级别搜索测试 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 测试组合列表 (类型, 级别)
    combinations = [
        ("景区", "5A景区"),
        ("景区", "4A景区"),
        ("景区", "3A景区"),
        ("景区", "2A景区"),
        ("景区", "省级"),  # 特别关注这个组合
        ("博物馆", "国家级"),
        ("博物馆", "省级"),
        ("地质公园", "世界级"),
        ("地质公园", "国家级"),
        ("地质公园", "省级"),
        ("森林公园", "国家级"),
        ("森林公园", "省级"),
        ("水利风景区", "是"),
        ("水利风景区", "否"),
        ("湿地风景区", "国际级"),
        ("湿地风景区", "国家级"),
        ("文物保护单位", "国家级"),
        ("文物保护单位", "省级"),
        ("自然保护区", "国家级"),
        ("自然保护区", "省级")
    ]
    
    results = {}
    
    for scenic_type, level in combinations:
        print(f"\n正在测试: 类型={scenic_type}, 级别={level}")
        
        params = {
            "type": scenic_type,
            "level": level,
            "page": 1,
            "page_size": 20  # 获取更多结果用于分析
        }
        
        try:
            response = requests.get(f"{BASE_URL}{SEARCH_ENDPOINT}", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查是否有结果
                if "results" in data and isinstance(data["results"], list):
                    result_count = len(data["results"])
                    total_count = data.get("total", result_count)
                    
                    print(f"  状态码: 200")
                    print(f"  当前页结果数: {result_count}")
                    print(f"  总结果数: {total_count}")
                    
                    results[f"{scenic_type}:{level}"] = {
                        "status": "success",
                        "count": total_count,
                        "first_page_count": result_count
                    }
                    
                    # 检查第一个结果的详细信息
                    if result_count > 0:
                        first_result = data["results"][0]
                        print(f"  第一个结果:")
                        print(f"    ID: {first_result.get('scenic_id')}")
                        print(f"    名称: {first_result.get('name')}")
                        print(f"    类型: {first_result.get('type')}")
                        print(f"    级别: {first_result.get('level')}")
                        print(f"    原始类型: {first_result.get('scenic_type_original', '')}")
                        
                        # 检查结果是否真的匹配搜索条件
                        type_match = scenic_type.lower() in first_result.get('type', '').lower()
                        level_match = level.lower() in first_result.get('level', '').lower()
                        
                        if not type_match:
                            print(f"  ⚠️ 警告: 第一个结果的类型 '{first_result.get('type')}' 似乎不包含搜索类型 '{scenic_type}'")
                        
                        if not level_match:
                            print(f"  ⚠️ 警告: 第一个结果的级别 '{first_result.get('level')}' 似乎不包含搜索级别 '{level}'")
                        
                        # 检查原始类型字段中是否包含类型:级别的格式
                        original_type = first_result.get('scenic_type_original', '')
                        expected_format = f"{scenic_type}:{level}"
                        if scenic_type == "景区" and level in ["5A景区", "4A景区", "3A景区", "2A景区"]:
                            # A级景区特殊处理
                            if level not in original_type:
                                print(f"  ⚠️ 警告: 原始类型 '{original_type}' 中没有找到 '{level}'")
                        elif expected_format not in original_type:
                            print(f"  ⚠️ 警告: 原始类型 '{original_type}' 中没有找到 '{expected_format}'")
                    else:
                        print("  没有找到任何结果")
                elif isinstance(data, list):
                    # 如果直接返回数组
                    result_count = len(data)
                    print(f"  状态码: 200")
                    print(f"  结果数: {result_count}")
                    
                    results[f"{scenic_type}:{level}"] = {
                        "status": "success",
                        "count": result_count,
                        "first_page_count": result_count
                    }
                    
                    if result_count > 0:
                        first_result = data[0]
                        print(f"  第一个结果:")
                        print(f"    ID: {first_result.get('scenic_id')}")
                        print(f"    名称: {first_result.get('name')}")
                        print(f"    类型: {first_result.get('type')}")
                        print(f"    级别: {first_result.get('level')}")
                    else:
                        print("  没有找到任何结果")
                else:
                    print(f"  状态码: 200，但返回了未预期的数据格式")
                    print(f"  返回数据: {data}")
                    
                    results[f"{scenic_type}:{level}"] = {
                        "status": "invalid_format",
                        "data": str(data)[:100] + "..."  # 只保留前100个字符
                    }
            else:
                print(f"  状态码: {response.status_code}")
                print(f"  错误信息: {response.text}")
                
                results[f"{scenic_type}:{level}"] = {
                    "status": "error",
                    "code": response.status_code,
                    "message": response.text
                }
                
        except Exception as e:
            print(f"  请求异常: {str(e)}")
            results[f"{scenic_type}:{level}"] = {
                "status": "exception",
                "message": str(e)
            }
        
        # 睡眠一小段时间，避免请求过快
        time.sleep(0.5)
    
    # 总结测试结果
    print("\n=== 测试结果总结 ===")
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    empty_count = sum(1 for r in results.values() if r["status"] == "success" and r["count"] == 0)
    error_count = sum(1 for r in results.values() if r["status"] in ["error", "exception"])
    
    print(f"总测试组合: {len(combinations)}")
    print(f"成功请求: {success_count}")
    print(f"无结果组合: {empty_count}")
    print(f"请求失败: {error_count}")
    
    print("\n有数据的组合:")
    for comb, result in sorted(results.items(), key=lambda x: x[1].get("count", 0), reverse=True):
        if result["status"] == "success" and result.get("count", 0) > 0:
            print(f"  {comb}: {result['count']} 个结果")
    
    print("\n无数据的组合:")
    for comb, result in sorted(results.items()):
        if result["status"] == "success" and result.get("count", 0) == 0:
            print(f"  {comb}")
    
    if error_count > 0:
        print("\n失败的组合:")
        for comb, result in results.items():
            if result["status"] in ["error", "exception"]:
                print(f"  {comb}: {result.get('message', 'Unknown error')}")

def test_specific_search():
    """测试特定的景区类型和级别搜索"""
    print(f"\n=== 特定景区搜索测试 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 特别关注的是有省级景区的搜索
    params = {
        "type": "景区",
        "level": "省级",
        "page": 1,
        "page_size": 50  # 获取更多结果以便分析
    }
    
    try:
        print(f"发送请求: {BASE_URL}{SEARCH_ENDPOINT}?type={params['type']}&level={params['level']}")
        response = requests.get(f"{BASE_URL}{SEARCH_ENDPOINT}", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # 检查是否有结果
            if "results" in data and isinstance(data["results"], list):
                results = data["results"]
                total = data.get("total", len(results))
                
                print(f"状态码: 200")
                print(f"总结果数: {total}")
                print(f"当前页结果数: {len(results)}")
                
                if len(results) > 0:
                    # 详细分析返回的结果
                    print("\n结果分析:")
                    
                    # 检查每个结果的类型和级别
                    type_count = {}
                    level_count = {}
                    original_type_patterns = {}
                    
                    for i, item in enumerate(results):
                        result_type = item.get("type", "未知")
                        result_level = item.get("level", "未知")
                        original_type = item.get("scenic_type_original", "")
                        
                        # 统计类型和级别
                        type_count[result_type] = type_count.get(result_type, 0) + 1
                        level_count[result_level] = level_count.get(result_level, 0) + 1
                        
                        # 分析原始类型字段的模式
                        for part in original_type.split(","):
                            part = part.strip()
                            if part:
                                original_type_patterns[part] = original_type_patterns.get(part, 0) + 1
                        
                        # 打印前5个结果的详细信息
                        if i < 5:
                            print(f"\n结果 #{i+1}:")
                            print(f"  ID: {item.get('scenic_id')}")
                            print(f"  名称: {item.get('name')}")
                            print(f"  省份: {item.get('province')}")
                            print(f"  类型: {result_type}")
                            print(f"  级别: {result_level}")
                            print(f"  原始类型: {original_type}")
                    
                    # 打印统计信息
                    print("\n类型统计:")
                    for t, count in sorted(type_count.items(), key=lambda x: x[1], reverse=True):
                        print(f"  {t}: {count}个")
                    
                    print("\n级别统计:")
                    for l, count in sorted(level_count.items(), key=lambda x: x[1], reverse=True):
                        print(f"  {l}: {count}个")
                    
                    print("\n原始类型模式统计:")
                    for pattern, count in sorted(original_type_patterns.items(), key=lambda x: x[1], reverse=True):
                        if "省级" in pattern:  # 特别关注含有"省级"的模式
                            print(f"  {pattern}: {count}个 [包含省级]")
                        elif "景区" in pattern:  # 特别关注含有"景区"的模式
                            print(f"  {pattern}: {count}个 [包含景区]")
                else:
                    print("\n没有找到任何结果")
            else:
                print(f"状态码: 200，但返回了未预期的数据格式")
                print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {str(e)}")

if __name__ == "__main__":
    test_specific_search()
    print("\n" + "="*80 + "\n")
    test_scenic_type_level_combinations() 