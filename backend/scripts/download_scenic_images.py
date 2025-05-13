#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下载马蜂窝景区图片到本地并更新数据库
"""

import os
import sys
import time
import requests
import logging
import MySQLdb
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 将Django项目根目录添加到Python路径中
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'download_images.log'))
    ]
)
logger = logging.getLogger('image_downloader')

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
MAX_WORKERS = 8  # 同时下载的图片数量
TIMEOUT = 30  # 请求超时时间（秒）
DEFAULT_IMAGE = '/media/scenic_images/default.jpg'  # 默认图片路径（相对于Web根目录）
HTTP_RETRIES = 3  # HTTP请求重试次数

# 确保图片目录存在
os.makedirs(IMAGES_DIR, exist_ok=True)

# 创建带重试的会话
def create_session():
    session = requests.Session()
    retry = Retry(
        total=HTTP_RETRIES,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    # 添加浏览器代理头，避免被墙
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    })
    return session

# 下载单个图片
def download_image(session, scenic_id, image_url):
    """
    下载单个图片，返回本地路径和下载状态
    """
    if not image_url or not scenic_id:
        logger.warning(f"图片URL为空或景区ID为空: {scenic_id}, {image_url}")
        return None, False
    
    try:
        # 从URL中提取文件名和扩展名
        parsed_url = urllib.parse.urlparse(image_url)
        url_path = parsed_url.path
        
        # 获取扩展名
        _, ext = os.path.splitext(url_path)
        if not ext or ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = '.jpg'  # 默认使用.jpg扩展名
        
        # 生成文件名：scenic_id.ext
        filename = f"{scenic_id}{ext}"
        local_path = os.path.join(IMAGES_DIR, filename)
        
        # 如果文件已存在，检查大小确认是否有效
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            logger.info(f"图片已存在，跳过下载: {local_path}")
            # 返回相对路径
            return f"/media/scenic_images/{filename}", True
        
        # 下载图片
        logger.info(f"开始下载图片: {image_url} 为景区ID: {scenic_id}")
        response = session.get(image_url, timeout=TIMEOUT, stream=True)
        
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 检查文件是否下载成功
            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                logger.info(f"图片下载成功: {local_path}")
                # 返回相对路径
                return f"/media/scenic_images/{filename}", True
            else:
                logger.error(f"图片下载后文件大小为0: {local_path}")
                return None, False
        else:
            logger.error(f"下载图片失败，状态码: {response.status_code}, URL: {image_url}")
            return None, False
            
    except Exception as e:
        logger.exception(f"下载图片出错: {image_url}, 错误: {str(e)}")
        return None, False

# 更新数据库中的图片URL
def update_image_url(db_conn, scenic_id, local_path):
    try:
        cursor = db_conn.cursor()
        cursor.execute(
            "UPDATE summary_table SET 图片URL = %s WHERE 景区ID = %s",
            (local_path, scenic_id)
        )
        db_conn.commit()
        cursor.close()
        return True
    except Exception as e:
        logger.exception(f"更新数据库图片URL失败，景区ID: {scenic_id}, 错误: {str(e)}")
        db_conn.rollback()
        return False

# 下载默认图片（如果不存在）
def ensure_default_image():
    default_image_path = os.path.join(IMAGES_DIR, 'default.jpg')
    if not os.path.exists(default_image_path):
        try:
            # 使用一个通用的默认图片URL，或者拷贝项目中的默认图片
            default_image_url = "https://p1-q.mafengwo.net/s12/M00/F7/57/wKgED1vT7q-AVR12AAG1VefU_pU98.jpeg"
            session = create_session()
            response = session.get(default_image_url, timeout=TIMEOUT)
            with open(default_image_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"默认图片下载成功: {default_image_path}")
        except Exception as e:
            logger.exception(f"下载默认图片出错: {str(e)}")
            # 创建一个空白默认图片
            with open(default_image_path, 'wb') as f:
                f.write(b'')

# 主函数
def main():
    logger.info("开始下载景区图片并更新数据库")
    
    # 确保默认图片存在
    ensure_default_image()
    
    try:
        # 连接数据库
        conn = MySQLdb.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 获取总记录数
        cursor.execute("SELECT COUNT(*) FROM summary_table WHERE 图片URL LIKE %s", ("http%",))
        total_records = cursor.fetchone()[0]
        logger.info(f"需要处理的马蜂窝图片总数: {total_records}")
        
        # 分批次处理，避免内存占用过大
        batch_size = 500
        processed = 0
        success = 0
        failed = 0
        
        # 创建线程池
        session = create_session()
        
        for offset in range(0, total_records, batch_size):
            # 获取一批图片URL
            cursor.execute(
                "SELECT 景区ID, 图片URL FROM summary_table WHERE 图片URL LIKE %s LIMIT %s OFFSET %s",
                ("http%", batch_size, offset)
            )
            records = cursor.fetchall()
            
            if not records:
                logger.info(f"没有更多记录需要处理")
                break
            
            logger.info(f"正在处理第 {offset+1} 到 {offset+len(records)} 条记录")
            
            # 使用线程池下载图片
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                for scenic_id, image_url in records:
                    try:
                        # 下载图片
                        local_path, download_success = download_image(session, scenic_id, image_url)
                        
                        # 更新数据库
                        if download_success and local_path:
                            if update_image_url(conn, scenic_id, local_path):
                                success += 1
                            else:
                                failed += 1
                        else:
                            # 如果下载失败，更新为默认图片
                            if update_image_url(conn, scenic_id, DEFAULT_IMAGE):
                                logger.warning(f"图片下载失败，使用默认图片：ID {scenic_id}")
                                failed += 1
                            else:
                                failed += 1
                                
                    except Exception as e:
                        logger.exception(f"处理记录出错，景区ID: {scenic_id}, 错误: {str(e)}")
                        failed += 1
                    
                    processed += 1
                    
                    # 每处理100条记录输出一次进度
                    if processed % 100 == 0:
                        logger.info(f"已处理: {processed}/{total_records}, 成功: {success}, 失败: {failed}")
                    
                    # 添加小的延迟，避免请求过快被封
                    time.sleep(0.2)
        
        cursor.close()
        conn.close()
        
        logger.info(f"图片下载完成! 总记录数: {total_records}, 处理: {processed}, 成功: {success}, 失败: {failed}")
        
    except Exception as e:
        logger.exception(f"主程序出错: {str(e)}")
    
if __name__ == "__main__":
    main() 