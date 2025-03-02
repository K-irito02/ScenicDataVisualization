#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
马蜂窝景点爬虫启动脚本（数据库存储URL版本）
用于初始化Redis数据库并启动爬虫
支持北京景点爬虫和全国景点爬虫
"""

import os
import sys
import time
import redis
import argparse
import subprocess
from datetime import datetime

def check_redis_connection(host='localhost', port=6379, db=0, password=None):
    """检查Redis连接是否正常"""
    try:
        r = redis.Redis(host=host, port=port, db=db, password=password)
        r.ping()
        print(f"[+] Redis连接成功: {host}:{port}")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"[-] Redis连接失败: {str(e)}")
        return None

def clear_redis_data(r, spider_name, clear_all=False):
    """清空Redis中的爬虫数据"""
    # 清空URL队列
    if spider_name == "beijing_attractions_db":
        r.delete(f"{spider_name}:list_urls")
        r.delete(f"{spider_name}:detail_urls")
        
        if clear_all:
            # 清空所有景点数据
            keys = r.keys("beijing:attraction:*")
            if keys:
                r.delete(*keys)
            # 清空索引
            r.delete("beijing:attractions:all")
            print("[+] 已清空所有北京爬虫数据")
        else:
            print("[+] 已清空北京爬虫队列数据")
    elif spider_name == "china_attractions_db":
        r.delete(f"{spider_name}:cities_urls")
        r.delete(f"{spider_name}:list_urls")
        r.delete(f"{spider_name}:detail_urls")
        
        if clear_all:
            # 清空所有景点数据
            keys = r.keys("china:attraction:*")
            if keys:
                r.delete(*keys)
            # 清空城市数据
            city_keys = r.keys("china:city:*")
            if city_keys:
                r.delete(*city_keys)
            # 清空索引
            r.delete("china:attractions:all")
            print("[+] 已清空所有全国爬虫数据")
        else:
            print("[+] 已清空全国爬虫队列数据")

def start_crawler(spider_name, settings_file=None, log_file=None, job_dir=None, node_id=None, is_master=False, task_type=None, redis_host=None):
    """启动爬虫"""
    cmd = ["scrapy", "crawl", spider_name]
    
    if settings_file:
        cmd.extend(["-s", f"SETTINGS_MODULE=mafengwo.{settings_file}"])
    
    if job_dir:
        # 创建job_dir目录
        os.makedirs(job_dir, exist_ok=True)
        cmd.extend(["-s", f"JOBDIR={job_dir}"])
    
    if log_file:
        # 创建logs目录
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        cmd.extend(["--logfile", log_file])
    
    if node_id:
        cmd.extend(["-s", f"NODE_ID={node_id}"])
    
    if is_master:
        cmd.extend(["-s", "IS_MASTER=True"])
    
    if task_type:
        cmd.extend(["-s", f"TASK_TYPE={task_type}"])
    
    if redis_host:
        cmd.extend(["-s", f"REDIS_HOST={redis_host}"])
    
    print(f"[+] 启动爬虫: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(cmd)
        return process
    except Exception as e:
        print(f"[-] 启动爬虫失败: {str(e)}")
        return None

def monitor_redis(r, spider_name, interval=10):
    """监控Redis数据库状态"""
    try:
        while True:
            if spider_name == "beijing_attractions_db":
                # 获取列表页URL队列长度
                list_urls_count = r.llen(f"{spider_name}:list_urls")
                # 获取详情页URL队列长度
                detail_urls_count = r.llen(f"{spider_name}:detail_urls")
                # 获取已保存的景点数量
                attraction_count = r.scard("beijing:attractions:all")
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"列表页URL队列: {list_urls_count}, "
                      f"详情页URL队列: {detail_urls_count}, "
                      f"已保存的景点: {attraction_count}")
            elif spider_name == "china_attractions_db":
                # 获取城市列表页URL队列长度
                cities_urls_count = r.llen(f"{spider_name}:cities_urls")
                # 获取列表页URL队列长度
                list_urls_count = r.llen(f"{spider_name}:list_urls")
                # 获取详情页URL队列长度
                detail_urls_count = r.llen(f"{spider_name}:detail_urls")
                # 获取已保存的景点数量
                attraction_count = r.scard("china:attractions:all")
                # 获取已保存的城市数量
                city_count = len(r.keys("china:city:info:*"))
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"城市列表页URL队列: {cities_urls_count}, "
                      f"景点列表页URL队列: {list_urls_count}, "
                      f"详情页URL队列: {detail_urls_count}, "
                      f"已保存的城市: {city_count}, "
                      f"已保存的景点: {attraction_count}")
            
            # 如果所有队列都为空且已经有景点数据，可能爬虫已经完成
            if spider_name == "beijing_attractions_db":
                if list_urls_count == 0 and detail_urls_count == 0 and attraction_count > 0:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 所有队列为空，爬虫可能已完成")
            elif spider_name == "china_attractions_db":
                if cities_urls_count == 0 and list_urls_count == 0 and detail_urls_count == 0 and attraction_count > 0:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 所有队列为空，爬虫可能已完成")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[!] 监控已停止")

def run_python_script(script_path):
    """运行Python脚本"""
    try:
        process = subprocess.Popen([sys.executable, script_path])
        return process
    except Exception as e:
        print(f"[-] 运行脚本失败: {str(e)}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="马蜂窝景点爬虫启动脚本")
    parser.add_argument("--spider", type=str, default="beijing_attractions_db", 
                        choices=["beijing_attractions_db", "china_attractions_db"],
                        help="要运行的爬虫名称")
    parser.add_argument("--redis-host", type=str, default="localhost", help="Redis服务器地址")
    parser.add_argument("--redis-port", type=int, default=6379, help="Redis服务器端口")
    parser.add_argument("--redis-db", type=int, default=0, help="Redis数据库编号")
    parser.add_argument("--redis-password", type=str, default="3143285505", help="Redis密码")
    parser.add_argument("--clear", action="store_true", help="清空Redis中的爬虫队列数据")
    parser.add_argument("--clear-all", action="store_true", help="清空Redis中的所有爬虫数据")
    parser.add_argument("--monitor", action="store_true", help="监控Redis数据库状态")
    parser.add_argument("--node-id", type=str, default="node1", help="节点ID")
    parser.add_argument("--master", action="store_true", help="是否为主节点")
    parser.add_argument("--task-type", type=str, default="all", 
                        choices=["all", "cities", "list", "detail"],
                        help="任务类型")
    parser.add_argument("--settings", type=str, default="settings_distributed", help="设置文件名")
    parser.add_argument("--log-file", type=str, help="日志文件路径")
    parser.add_argument("--job-dir", type=str, help="任务目录路径")
    parser.add_argument("--export", action="store_true", help="导出数据")
    
    args = parser.parse_args()
    
    # 检查Redis连接
    r = check_redis_connection(
        host=args.redis_host,
        port=args.redis_port,
        db=args.redis_db,
        password=args.redis_password
    )
    
    if not r:
        print("[-] 无法连接到Redis，请检查配置")
        return
    
    # 清空Redis数据
    if args.clear or args.clear_all:
        clear_redis_data(r, args.spider, args.clear_all)
        if not args.monitor:  # 如果不需要监控，则退出
            return
    
    # 导出数据
    if args.export:
        export_script = os.path.join(os.path.dirname(__file__), "export_data.py")
        if os.path.exists(export_script):
            print(f"[+] 运行数据导出脚本: {export_script}")
            run_python_script(export_script)
        else:
            print(f"[-] 数据导出脚本不存在: {export_script}")
        return
    
    # 设置日志文件
    if not args.log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.log_file = f"logs/{args.spider}_{args.node_id}_{timestamp}.log"
    
    # 设置任务目录
    if not args.job_dir:
        args.job_dir = f"crawls/{args.spider}_{args.node_id}"
    
    # 启动爬虫
    process = start_crawler(
        spider_name=args.spider,
        settings_file=args.settings,
        log_file=args.log_file,
        job_dir=args.job_dir,
        node_id=args.node_id,
        is_master=args.master,
        task_type=args.task_type,
        redis_host=args.redis_host
    )
    
    # 监控Redis状态
    if args.monitor and process:
        try:
            monitor_redis(r, args.spider)
        except KeyboardInterrupt:
            print("\n[!] 程序已停止")
            if process:
                process.terminate()

if __name__ == "__main__":
    main() 