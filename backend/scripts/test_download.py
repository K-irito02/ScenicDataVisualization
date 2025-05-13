#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试下载脚本 - 只下载前5张图片并更新数据库
"""

import os
import sys
import MySQLdb
import requests
import logging
import time
import urllib.parse

# 将Django项目根目录添加到Python路径中
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_downloader')

# 配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Smg.2025',
    'db': 'scenic_area',
    'charset': 'utf8mb4'
}

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')
IMAGES_DIR = os.path.join(MEDIA_ROOT, 'scenic_images')

# 确保图片目录存在
os.makedirs(IMAGES_DIR, exist_ok=True)

def download_image(scenic_id, image_url):
    """下载单个图片并返回本地路径"""
    try:
        # 获取扩展名
        _, ext = os.path.splitext(urllib.parse.urlparse(image_url).path)
        if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = '.jpg'
            
        filename = f"{scenic_id}{ext}"
        local_path = os.path.join(IMAGES_DIR, filename)
        
        logger.info(f"下载图片: {image_url} 为ID: {scenic_id}")
        response = requests.get(image_url, timeout=30)
        
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"图片保存到: {local_path}")
            return f"/media/scenic_images/{filename}"
        else:
            logger.error(f"下载失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        logger.exception(f"下载出错: {e}")
        return None

def update_database(conn, scenic_id, local_path):
    """更新数据库中的图片URL"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE summary_table SET 图片URL = %s WHERE 景区ID = %s",
            (local_path, scenic_id)
        )
        conn.commit()
        logger.info(f"更新数据库成功，ID: {scenic_id}, 路径: {local_path}")
        cursor.close()
        return True
    except Exception as e:
        logger.exception(f"更新数据库出错: {e}")
        conn.rollback()
        return False

def main():
    try:
        # 连接数据库
        conn = MySQLdb.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 获取前5个图片URL
        cursor.execute(
            "SELECT 景区ID, 图片URL FROM summary_table WHERE 图片URL LIKE 'http%' LIMIT 5"
        )
        records = cursor.fetchall()
        
        logger.info(f"找到 {len(records)} 个图片记录进行测试下载")
        
        for scenic_id, image_url in records:
            local_path = download_image(scenic_id, image_url)
            if local_path:
                update_database(conn, scenic_id, local_path)
            time.sleep(1)  # 小暂停，避免请求过快
        
        cursor.close()
        conn.close()
        
        logger.info("测试完成!")
        
    except Exception as e:
        logger.exception(f"测试出错: {e}")

if __name__ == "__main__":
    main()