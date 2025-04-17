import requests
import json
import time
from datetime import datetime

# 测试URL
BASE_URL = "http://localhost:8000/api"
SEARCH_ENDPOINT = "/scenic/search/"

def test_browser_requests():
    """模拟浏览器发送的网络请求，检查响应结果处理"""
    print(f"=== 浏览器网络请求模拟测试 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 测试场景
    test_cases = [
        {
            "name": "A级景区-省级 (模拟浏览器GET请求)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": "http://localhost:8080/",
                "Connection": "keep-alive"
            },
            "params": {
                "keyword": "",
                "province": "",
                "city": "",
                "district": "",
                "type": "景区",  # 前端显示A级景区，但实际传递"景区"
                "level": "省级",
                "priceRange": "0,500",
                "page": "1",
                "page_size": "12"
            }
        },
        {
            "name": "5A景区搜索 (模拟浏览器GET请求)",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": "http://localhost:8080/",
                "Connection": "keep-alive"
            },
            "params": {
                "keyword": "",
                "province": "",
                "city": "",
                "district": "",
                "type": "景区",
                "level": "5A景区",
                "priceRange": "0,500",
                "page": "1",
                "page_size": "12"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n测试用例 {i+1}: {test_case['name']}")
        print(f"请求参数: {json.dumps(test_case['params'], ensure_ascii=False)}")
        
        try:
            # 发送带有浏览器头的HTTP请求
            start_time = time.time()
            response = requests.get(
                f"{BASE_URL}{SEARCH_ENDPOINT}", 
                params=test_case['params'],
                headers=test_case['headers'],
                timeout=10
            )
            response_time = time.time() - start_time
            
            print(f"请求URL: {response.url}")
            print(f"响应时间: {response_time:.2f}秒")
            
            if response.status_code == 200:
                data = response.json()
                
                # 分析响应内容
                if "results" in data and isinstance(data["results"], list):
                    results = data["results"]
                    total_count = data.get("total", 0)
                    page = data.get("page", 1)
                    pages = data.get("pages", 1)
                    
                    print(f"状态码: 200")
                    print(f"总结果数: {total_count}")
                    print(f"总页数: {pages}")
                    print(f"当前页: {page}")
                    print(f"当前页结果数: {len(results)}")
                    
                    # 分析搜索结果的匹配情况
                    if len(results) > 0:
                        type_matched = 0
                        level_matched = 0
                        both_matched = 0
                        
                        search_type = test_case['params']['type']
                        search_level = test_case['params']['level']
                        
                        for result in results:
                            result_type = result.get('type', '')
                            result_level = result.get('level', '')
                            
                            type_match = (search_type.lower() in result_type.lower())
                            level_match = (search_level.lower() in result_level.lower())
                            
                            if type_match:
                                type_matched += 1
                            if level_match:
                                level_matched += 1
                            if type_match and level_match:
                                both_matched += 1
                        
                        print(f"\n匹配分析:")
                        print(f"  类型匹配数: {type_matched}/{len(results)} ({type_matched/len(results)*100:.1f}%)")
                        print(f"  级别匹配数: {level_matched}/{len(results)} ({level_matched/len(results)*100:.1f}%)")
                        print(f"  完全匹配数: {both_matched}/{len(results)} ({both_matched/len(results)*100:.1f}%)")
                        
                        # 打印前3条结果的详细信息
                        print("\n结果示例:")
                        for i, result in enumerate(results[:3]):
                            print(f"\n结果 #{i+1}:")
                            print(f"  ID: {result.get('scenic_id')}")
                            print(f"  名称: {result.get('name')}")
                            print(f"  类型: {result.get('type')}")
                            print(f"  级别: {result.get('level')}")
                            print(f"  省份: {result.get('province')}")
                            print(f"  原始类型: {result.get('scenic_type_original', '')}")
                            
                            # 检查匹配情况
                            type_match = (search_type.lower() in result.get('type', '').lower())
                            level_match = (search_level.lower() in result.get('level', '').lower())
                            print(f"  类型匹配: {'✓' if type_match else '✗'}")
                            print(f"  级别匹配: {'✓' if level_match else '✗'}")
                    else:
                        print("没有找到匹配的结果")
                        
                        # 尝试不带级别再搜索一次，看是否有结果
                        print("\n尝试仅搜索类型，不指定级别:")
                        alt_params = test_case['params'].copy()
                        alt_params.pop('level', None)
                        
                        alt_response = requests.get(
                            f"{BASE_URL}{SEARCH_ENDPOINT}", 
                            params=alt_params,
                            headers=test_case['headers'],
                            timeout=10
                        )
                        
                        if alt_response.status_code == 200:
                            alt_data = alt_response.json()
                            if "results" in alt_data and isinstance(alt_data["results"], list):
                                alt_results = alt_data["results"]
                                print(f"  仅搜索类型得到结果数: {len(alt_results)}")
                                if len(alt_results) > 0:
                                    print(f"  说明数据库中存在该类型景区，但可能没有指定级别的景区")
                elif isinstance(data, list):
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
        
        print("-" * 80)
        time.sleep(0.5)  # 避免请求过快

def check_browser_and_api_dataformat():
    """检查浏览器请求和API直接调用的数据格式区别"""
    print(f"=== 浏览器请求与API直接调用数据格式比较 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    
    # 测试参数
    params = {
        "type": "景区",
        "level": "省级",
        "page": "1",
        "page_size": "12"
    }
    
    # 浏览器请求头
    browser_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "http://localhost:8080/",
        "Connection": "keep-alive"
    }
    
    # 默认API请求头
    api_headers = {
        "Accept": "application/json"
    }
    
    print("\n1. 模拟浏览器请求:")
    try:
        browser_response = requests.get(
            f"{BASE_URL}{SEARCH_ENDPOINT}", 
            params=params,
            headers=browser_headers,
            timeout=10
        )
        
        print(f"请求URL: {browser_response.url}")
        
        if browser_response.status_code == 200:
            browser_data = browser_response.json()
            print(f"响应状态码: 200")
            
            # 检查响应数据格式
            if "results" in browser_data:
                print(f"数据格式: 包含results字段的对象")
                print(f"结果数量: {len(browser_data['results'])}")
                print(f"总结果数: {browser_data.get('total', '未提供')}")
                print(f"总页数: {browser_data.get('pages', '未提供')}")
                
                # 打印响应头
                print("\n响应头:")
                for key, value in browser_response.headers.items():
                    print(f"  {key}: {value}")
            else:
                print(f"数据格式: {type(browser_data).__name__}")
                print(f"数据长度: {len(browser_data) if isinstance(browser_data, (list, dict)) else '不适用'}")
        else:
            print(f"响应状态码: {browser_response.status_code}")
            print(f"错误信息: {browser_response.text}")
    except Exception as e:
        print(f"浏览器请求异常: {str(e)}")
    
    print("\n2. API直接调用:")
    try:
        api_response = requests.get(
            f"{BASE_URL}{SEARCH_ENDPOINT}", 
            params=params,
            headers=api_headers,
            timeout=10
        )
        
        print(f"请求URL: {api_response.url}")
        
        if api_response.status_code == 200:
            api_data = api_response.json()
            print(f"响应状态码: 200")
            
            # 检查响应数据格式
            if "results" in api_data:
                print(f"数据格式: 包含results字段的对象")
                print(f"结果数量: {len(api_data['results'])}")
                print(f"总结果数: {api_data.get('total', '未提供')}")
                print(f"总页数: {api_data.get('pages', '未提供')}")
                
                # 打印响应头
                print("\n响应头:")
                for key, value in api_response.headers.items():
                    print(f"  {key}: {value}")
            else:
                print(f"数据格式: {type(api_data).__name__}")
                print(f"数据长度: {len(api_data) if isinstance(api_data, (list, dict)) else '不适用'}")
        else:
            print(f"响应状态码: {api_response.status_code}")
            print(f"错误信息: {api_response.text}")
    except Exception as e:
        print(f"API调用异常: {str(e)}")
    
    # 比较两次请求结果
    if 'browser_data' in locals() and 'api_data' in locals():
        print("\n比较两次请求结果:")
        browser_format = "包含results字段的对象" if "results" in browser_data else type(browser_data).__name__
        api_format = "包含results字段的对象" if "results" in api_data else type(api_data).__name__
        
        print(f"浏览器请求数据格式: {browser_format}")
        print(f"API调用数据格式: {api_format}")
        
        if browser_format == api_format:
            print("两种请求返回相同的数据格式")
            
            if "results" in browser_data and "results" in api_data:
                browser_count = len(browser_data["results"])
                api_count = len(api_data["results"])
                
                print(f"浏览器请求结果数: {browser_count}")
                print(f"API调用结果数: {api_count}")
                
                if browser_count == api_count:
                    print("两种请求返回相同数量的结果")
                    
                    # 检查前3条结果是否一致
                    if browser_count > 0:
                        same_results = True
                        for i in range(min(3, browser_count)):
                            browser_result = browser_data["results"][i]
                            api_result = api_data["results"][i]
                            
                            if browser_result.get("scenic_id") != api_result.get("scenic_id"):
                                same_results = False
                                break
                        
                        print(f"前3条结果一致: {'是' if same_results else '否'}")
                else:
                    print("两种请求返回不同数量的结果，可能存在问题")
        else:
            print("两种请求返回不同的数据格式，可能存在问题")

if __name__ == "__main__":
    test_browser_requests()
    print("\n" + "="*80 + "\n")
    check_browser_and_api_dataformat() 