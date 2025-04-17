import os
import sys
import time
import subprocess
from datetime import datetime

def print_header(title):
    """打印带有格式的标题"""
    border = "=" * (len(title) + 4)
    print(f"\n{border}")
    print(f"= {title} =")
    print(f"{border}\n")

def run_test(script_name, description):
    """运行指定的测试脚本"""
    print_header(description)
    
    # 构建命令
    if sys.platform == 'win32':
        command = f"python \"Backend API Test Scripts\\{script_name}\""
    else:
        command = f"python \"Backend API Test Scripts/{script_name}\""
    
    # 执行命令
    print(f"执行脚本: {script_name}")
    print(f"命令: {command}\n")
    
    try:
        # 使用subprocess运行命令并实时输出结果
        process = subprocess.Popen(
            command, 
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 实时输出结果
        for line in process.stdout:
            print(line, end='')
        
        # 等待进程完成
        return_code = process.wait()
        
        if return_code == 0:
            print(f"\n✅ 测试成功完成")
        else:
            print(f"\n❌ 测试失败，返回码: {return_code}")
    
    except Exception as e:
        print(f"\n❌ 执行测试时出错: {str(e)}")
    
    print("\n" + "-" * 80 + "\n")

def main():
    """主函数，运行所有测试"""
    print_header(f"景区搜索测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 确保测试脚本目录存在
    os.makedirs("Backend API Test Scripts", exist_ok=True)
    
    # 要运行的测试脚本
    tests = [
        {
            "script": "ScenicType_LevelTest.py",
            "description": "景区类型和级别组合测试"
        },
        {
            "script": "Frontend_SearchTest.py",
            "description": "前端搜索模拟测试"
        },
        {
            "script": "Frontend_NetworkTest.py",
            "description": "前端网络请求模拟测试"
        }
    ]
    
    # 运行所有测试
    for test in tests:
        run_test(test["script"], test["description"])
    
    print_header("所有测试已完成")

if __name__ == "__main__":
    main() 