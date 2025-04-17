import requests
import json
import time
from datetime import datetime

# 测试URL
BASE_URL = "http://localhost:8000/api"
SEARCH_ENDPOINT = "/scenic/search/"

def test_frontend_search():
    """模拟前端进行的景区搜索"""
    print(f"=== 前端搜索模拟测试 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 模拟前端界面常见的搜索场景
    test_cases = [
        {
            "name": "A级景区-省级搜索",
            "params": {
                "type": "景区",  # 前端显示"A级景区"，实际传递"景区"
                "level": "省级",
                "page": 1,
                "page_size": 12
            }
        },
        {
            "name": "A级景区-5A级搜索",
            "params": {
                "type": "景区",
                "level": "5A景区",
                "page": 1,
                "page_size": 12
            }
        },
        {
            "name": "文物保护单位-省级搜索",
            "params": {
                "type": "文物保护单位",
                "level": "省级",
                "page": 1,
                "page_size": 12
            }
        },
        {
            "name": "水利风景区-是搜索",
            "params": {
                "type": "水利风景区",
                "level": "是",
                "page": 1,
                "page_size": 12
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试用例: {test_case['name']}")
        print(f"请求参数: {test_case['params']}")
        
        try:
            # 发送HTTP请求
            response = requests.get(
                f"{BASE_URL}{SEARCH_ENDPOINT}", 
                params=test_case['params'],
                timeout=10
            )
            
            print(f"请求URL: {response.url}")
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查响应格式
                if "results" in data and isinstance(data["results"], list):
                    results = data["results"]
                    total_count = data.get("total", len(results))
                    current_page = data.get("page", 1)
                    pages = data.get("pages", 1)
                    
                    print(f"状态码: 200")
                    print(f"总结果数: {total_count}")
                    print(f"当前页: {current_page}/{pages}")
                    print(f"本页结果数: {len(results)}")
                    
                    # 分析返回的结果
                    if len(results) > 0:
                        # 统计类型和级别
                        type_stats = {}
                        level_stats = {}
                        
                        for result in results:
                            result_type = result.get("type", "未知")
                            result_level = result.get("level", "未知")
                            
                            type_stats[result_type] = type_stats.get(result_type, 0) + 1
                            level_stats[result_level] = level_stats.get(result_level, 0) + 1
                        
                        print("\n类型统计:")
                        for type_name, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
                            print(f"  {type_name}: {count}个")
                        
                        print("\n级别统计:")
                        for level_name, count in sorted(level_stats.items(), key=lambda x: x[1], reverse=True):
                            print(f"  {level_name}: {count}个")
                        
                        # 检查第一条结果
                        first_result = results[0]
                        print("\n第一条结果:")
                        print(f"  景区ID: {first_result.get('scenic_id')}")
                        print(f"  名称: {first_result.get('name')}")
                        print(f"  类型: {first_result.get('type')}")
                        print(f"  级别: {first_result.get('level')}")
                        print(f"  原始类型: {first_result.get('scenic_type_original')}")
                        
                        # 特别检查：是否与搜索条件匹配
                        search_type = test_case['params']['type']
                        search_level = test_case['params']['level']
                        
                        # 检查类型匹配
                        type_match = (search_type.lower() in first_result.get('type', '').lower())
                        # 检查级别匹配
                        level_match = (search_level.lower() in first_result.get('level', '').lower())
                        
                        # 打印匹配结果
                        print("\n搜索条件匹配分析:")
                        print(f"  类型匹配: {'✓' if type_match else '✗'} (搜索:{search_type}, 结果:{first_result.get('type')})")
                        print(f"  级别匹配: {'✓' if level_match else '✗'} (搜索:{search_level}, 结果:{first_result.get('level')})")
                        
                    else:
                        print("没有找到匹配的结果")
                elif isinstance(data, list):
                    # 如果直接返回的是结果数组
                    print(f"状态码: 200")
                    print(f"结果数量: {len(data)}")
                    
                    if len(data) > 0:
                        print("\n第一条结果:")
                        print(f"  景区ID: {data[0].get('scenic_id')}")
                        print(f"  名称: {data[0].get('name')}")
                        print(f"  类型: {data[0].get('type')}")
                        print(f"  级别: {data[0].get('level')}")
                    else:
                        print("没有找到匹配的结果")
                else:
                    print(f"状态码: 200，但返回了未预期的数据格式")
                    print(f"返回数据: {json.dumps(data, ensure_ascii=False)[:200]}...")
            else:
                print(f"状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"请求异常: {str(e)}")
        
        print("-" * 60)
        time.sleep(0.5)  # 避免请求过快

def test_frontend_vs_backend_format():
    """测试前端和后端参数格式的区别"""
    print(f"=== 前端与后端参数格式比较测试 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 前端格式 (A级景区 -> 景区)
    frontend_params = {
        "type": "景区",  # 前端显示A级景区，但实际发送"景区"
        "level": "省级",
        "page": 1,
        "page_size": 12
    }
    
    # 可能的后端理解格式
    backend_params = {
        "type": "景区",
        "level": "省级",
        "page": 1,
        "page_size": 12
    }
    
    # 测试前端格式
    print("\n测试前端格式参数:")
    print(f"参数: {frontend_params}")
    
    try:
        frontend_response = requests.get(
            f"{BASE_URL}{SEARCH_ENDPOINT}", 
            params=frontend_params,
            timeout=10
        )
        
        print(f"请求URL: {frontend_response.url}")
        
        if frontend_response.status_code == 200:
            frontend_data = frontend_response.json()
            
            if "results" in frontend_data:
                print(f"成功: 前端格式返回了 {len(frontend_data['results'])} 条结果，总计 {frontend_data.get('total', 0)} 条")
            elif isinstance(frontend_data, list):
                print(f"成功: 前端格式返回了 {len(frontend_data)} 条结果")
            else:
                print(f"成功但格式异常: {frontend_data}")
        else:
            print(f"错误: 状态码 {frontend_response.status_code}")
            print(f"错误信息: {frontend_response.text}")
    except Exception as e:
        print(f"前端格式请求异常: {str(e)}")
    
    # 测试后端格式
    print("\n测试后端格式参数:")
    print(f"参数: {backend_params}")
    
    try:
        backend_response = requests.get(
            f"{BASE_URL}{SEARCH_ENDPOINT}", 
            params=backend_params,
            timeout=10
        )
        
        print(f"请求URL: {backend_response.url}")
        
        if backend_response.status_code == 200:
            backend_data = backend_response.json()
            
            if "results" in backend_data:
                print(f"成功: 后端格式返回了 {len(backend_data['results'])} 条结果，总计 {backend_data.get('total', 0)} 条")
            elif isinstance(backend_data, list):
                print(f"成功: 后端格式返回了 {len(backend_data)} 条结果")
            else:
                print(f"成功但格式异常: {backend_data}")
        else:
            print(f"错误: 状态码 {backend_response.status_code}")
            print(f"错误信息: {backend_response.text}")
    except Exception as e:
        print(f"后端格式请求异常: {str(e)}")
    
    # 比较两种格式的结果
    if 'frontend_data' in locals() and 'backend_data' in locals():
        frontend_count = len(frontend_data.get('results', [])) if isinstance(frontend_data, dict) else len(frontend_data)
        backend_count = len(backend_data.get('results', [])) if isinstance(backend_data, dict) else len(backend_data)
        
        print(f"\n结果比较:")
        print(f"前端格式返回结果数: {frontend_count}")
        print(f"后端格式返回结果数: {backend_count}")
        
        if frontend_count != backend_count:
            print("警告: 两种格式返回的结果数不同!")
        else:
            print("两种格式返回相同数量的结果")
            
if __name__ == "__main__":
    test_frontend_search()
    print("\n" + "="*80 + "\n")
    test_frontend_vs_backend_format() 