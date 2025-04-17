"""
测试省份城市景区分布API的脚本
"""
import json
import os
import django
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # 恢复原来的设置模块路径
django.setup()

# 导入必要的模块
from django.db.models import Count
from django.test.client import RequestFactory
from scenic_data.models import ScenicData
from scenic_data.views import ProvinceCityDistributionView

def main():
    # 解析命令行参数，支持指定测试的省份
    test_province = "北京市"  # 默认测试北京市
    
    # 检查是否提供了命令行参数
    if len(sys.argv) > 1:
        arg_index = 0
        for i, arg in enumerate(sys.argv):
            if arg == "--test-province" and i + 1 < len(sys.argv):
                test_province = sys.argv[i + 1]
                break
            elif arg.startswith("--test-province="):
                parts = arg.split("=", 1)
                if len(parts) > 1:
                    test_province = parts[1]
                break
    
    print("\n" + "=" * 50)
    print("测试方法1: 直接使用ORM查询")
    print("=" * 50)
    
    # 检查省份是否存在
    province_exists = ScenicData.objects.filter(province=test_province).exists()
    print(f"省份 {test_province} 存在景区数据: {province_exists}")
    
    if province_exists:
        print(f"\n{test_province}的城市景区分布:")
        city_counts = ScenicData.objects.filter(province=test_province)\
            .values('city')\
            .annotate(count=Count('scenic_id'))\
            .order_by('-count')
        
        for city in city_counts:
            if city['city']:  # 跳过城市名为空的记录
                print(f"{city['city']}: {city['count']}个景区")
    
    print("\n" + "=" * 50)
    print("测试方法2: 使用视图函数测试API")
    print("=" * 50)
    
    # 创建请求工厂和请求
    factory = RequestFactory()
    request = factory.get(f'/data/province-city-distribution/{test_province}/')
    
    # 调用视图函数
    view = ProvinceCityDistributionView.as_view()
    response = view(request, province_name=test_province)
    
    # 输出响应结果
    print(f"响应状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.data
        print(f"\n成功获取{test_province}的城市景区分布数据，共{len(data)}个城市")
        
        # 格式化输出结果
        print("\n城市景区数量排名:")
        for i, city in enumerate(data[:10], 1):  # 只显示前10个
            print(f"{i}. {city['name']}: {city['value']}个景区")
        
        if len(data) > 10:
            print(f"... 还有{len(data)-10}个城市未显示")
        
        # 显示第一个城市的景区详情
        if data and data[0]['scenics']:
            first_city = data[0]['name']
            scenics = data[0]['scenics']
            print(f"\n{first_city}的景区示例 (共{len(scenics)}个):")
            for i, scenic in enumerate(scenics[:5], 1):  # 只显示前5个
                print(f"{i}. {scenic['name']} (ID: {scenic['id']})")
                print(f"   坐标: 经度 {scenic['longitude']}, 纬度 {scenic['latitude']}")
            
            if len(scenics) > 5:
                print(f"... 还有{len(scenics)-5}个景区未显示")
        
        # 保存结果到JSON文件
        with open(f"{test_province}_city_distribution.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n已将完整结果保存到 {test_province}_city_distribution.json")
    else:
        print(f"请求失败: {response.data if hasattr(response, 'data') else '无详细信息'}")

if __name__ == "__main__":
    main() 