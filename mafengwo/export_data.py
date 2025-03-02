#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
马蜂窝景点数据导出脚本
从Redis数据库导出景点数据到JSON文件
支持北京景点爬虫和全国景点爬虫
"""

import os
import sys
import json
import redis
import argparse
from datetime import datetime

def connect_to_redis(host='localhost', port=6379, db=0, password=None):
    """连接到Redis数据库"""
    try:
        r = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)
        r.ping()
        print(f"[+] Redis连接成功: {host}:{port}")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"[-] Redis连接失败: {str(e)}")
        return None

def export_attractions_to_json(r, output_file, data_type='beijing'):
    """从Redis导出景点数据到JSON文件"""
    # 获取所有景点的键
    if data_type == 'beijing':
        attraction_keys = r.smembers('beijing:attractions:all')
    else:  # china
        attraction_keys = r.smembers('china:attractions:all')
    
    if not attraction_keys:
        print(f"[-] 未找到任何{data_type}景点数据")
        return False
    
    print(f"[+] 找到 {len(attraction_keys)} 个{data_type}景点数据")
    
    # 获取所有景点数据
    attractions = []
    for key in attraction_keys:
        data = r.get(key)
        if data:
            try:
                attraction = json.loads(data)
                attractions.append(attraction)
            except json.JSONDecodeError as e:
                print(f"[-] 解析景点数据失败 ({key}): {str(e)}")
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存到JSON文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(attractions, f, ensure_ascii=False, indent=4)
        print(f"[+] 成功导出 {len(attractions)} 个{data_type}景点数据到 {output_file}")
        return True
    except Exception as e:
        print(f"[-] 导出数据失败: {str(e)}")
        return False

def export_attractions_to_csv(r, output_file, data_type='beijing'):
    """从Redis导出景点数据到CSV文件"""
    import csv
    
    # 获取所有景点的键
    if data_type == 'beijing':
        attraction_keys = r.smembers('beijing:attractions:all')
    else:  # china
        attraction_keys = r.smembers('china:attractions:all')
    
    if not attraction_keys:
        print(f"[-] 未找到任何{data_type}景点数据")
        return False
    
    print(f"[+] 找到 {len(attraction_keys)} 个{data_type}景点数据")
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 定义CSV字段
    fieldnames = [
        'name', 'poi_id', 'city', 'city_id', 'score', 'location', 
        'summary', 'transport', 'ticket', 'opening_hours', 
        'image', 'link'
    ]
    
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # 获取所有景点数据并写入CSV
            count = 0
            for key in attraction_keys:
                data = r.get(key)
                if data:
                    try:
                        attraction = json.loads(data)
                        # 创建一个只包含CSV字段的字典
                        row = {field: attraction.get(field, '') for field in fieldnames}
                        # 处理特殊字段
                        if isinstance(row['ticket'], list):
                            row['ticket'] = ', '.join(row['ticket'])
                        writer.writerow(row)
                        count += 1
                    except (json.JSONDecodeError, Exception) as e:
                        print(f"[-] 处理景点数据失败 ({key}): {str(e)}")
            
            print(f"[+] 成功导出 {count} 个{data_type}景点数据到 {output_file}")
            return True
    except Exception as e:
        print(f"[-] 导出数据失败: {str(e)}")
        return False

def export_cities_to_json(r, output_file):
    """从Redis导出城市数据到JSON文件"""
    # 获取所有城市的键
    city_keys = r.keys('china:city:info:*')
    
    if not city_keys:
        print("[-] 未找到任何城市数据")
        return False
    
    print(f"[+] 找到 {len(city_keys)} 个城市数据")
    
    # 获取所有城市数据
    cities = []
    for key in city_keys:
        data = r.get(key)
        if data:
            try:
                city = json.loads(data)
                cities.append(city)
            except json.JSONDecodeError as e:
                print(f"[-] 解析城市数据失败 ({key}): {str(e)}")
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存到JSON文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cities, f, ensure_ascii=False, indent=4)
        print(f"[+] 成功导出 {len(cities)} 个城市数据到 {output_file}")
        return True
    except Exception as e:
        print(f"[-] 导出数据失败: {str(e)}")
        return False

def export_city_attractions_to_json(r, city_id, output_file):
    """从Redis导出指定城市的景点数据到JSON文件"""
    # 获取指定城市的所有景点键
    attraction_keys = r.smembers(f'china:city:{city_id}:attractions')
    
    if not attraction_keys:
        print(f"[-] 未找到城市ID为 {city_id} 的任何景点数据")
        return False
    
    print(f"[+] 找到城市ID为 {city_id} 的 {len(attraction_keys)} 个景点数据")
    
    # 获取城市信息
    city_info = None
    city_info_data = r.get(f'china:city:info:{city_id}')
    if city_info_data:
        try:
            city_info = json.loads(city_info_data)
        except json.JSONDecodeError:
            pass
    
    city_name = city_info['name'] if city_info else city_id
    
    # 获取所有景点数据
    attractions = []
    for key in attraction_keys:
        data = r.get(key)
        if data:
            try:
                attraction = json.loads(data)
                attractions.append(attraction)
            except json.JSONDecodeError as e:
                print(f"[-] 解析景点数据失败 ({key}): {str(e)}")
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存到JSON文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(attractions, f, ensure_ascii=False, indent=4)
        print(f"[+] 成功导出城市 {city_name} 的 {len(attractions)} 个景点数据到 {output_file}")
        return True
    except Exception as e:
        print(f"[-] 导出数据失败: {str(e)}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="马蜂窝景点数据导出脚本")
    
    # 添加命令行参数
    parser.add_argument("--redis-host", default="localhost",
                        help="Redis服务器地址")
    parser.add_argument("--redis-port", type=int, default=6379,
                        help="Redis服务器端口")
    parser.add_argument("--redis-db", type=int, default=0,
                        help="Redis数据库编号")
    parser.add_argument("--redis-password", default="3143285505",
                        help="Redis密码")
    parser.add_argument("--output", default=None,
                        help="输出文件路径")
    parser.add_argument("--format", choices=["json", "csv"], default="json",
                        help="输出文件格式 (json 或 csv)")
    parser.add_argument("--data-type", choices=["beijing", "china", "city"], default="beijing",
                        help="要导出的数据类型 (beijing=北京景点, china=全国景点, city=指定城市景点)")
    parser.add_argument("--city-id", default=None,
                        help="要导出的城市ID (仅当 --data-type=city 时有效)")
    parser.add_argument("--export-cities", action="store_true",
                        help="是否导出城市数据 (仅当 --data-type=china 时有效)")
    
    args = parser.parse_args()
    
    # 连接Redis
    r = connect_to_redis(
        host=args.redis_host,
        port=args.redis_port,
        db=args.redis_db,
        password=args.redis_password
    )
    
    if not r:
        print("[-] 无法连接到Redis，程序退出")
        sys.exit(1)
    
    # 默认输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 导出数据
    if args.data_type == "beijing":
        if not args.output:
            args.output = f"results/beijing_attractions_{timestamp}.{args.format}"
        
        if args.format == "json":
            success = export_attractions_to_json(r, args.output, 'beijing')
        else:  # csv
            success = export_attractions_to_csv(r, args.output, 'beijing')
    
    elif args.data_type == "china":
        if not args.output:
            args.output = f"results/china_attractions_{timestamp}.{args.format}"
        
        if args.format == "json":
            success = export_attractions_to_json(r, args.output, 'china')
        else:  # csv
            success = export_attractions_to_csv(r, args.output, 'china')
        
        # 导出城市数据
        if args.export_cities:
            cities_output = f"results/china_cities_{timestamp}.json"
            export_cities_to_json(r, cities_output)
    
    elif args.data_type == "city":
        if not args.city_id:
            print("[-] 导出城市景点数据时必须指定 --city-id 参数")
            sys.exit(1)
        
        if not args.output:
            args.output = f"results/city_{args.city_id}_attractions_{timestamp}.json"
        
        success = export_city_attractions_to_json(r, args.city_id, args.output)
    
    if success:
        print("[+] 数据导出完成")
    else:
        print("[-] 数据导出失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 