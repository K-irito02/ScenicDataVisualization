#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
from collections import Counter
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # 请根据实际情况修改用户名
    'password': '3143285505',  # 请根据实际情况修改密码
    'database': 'scenic_area',
    'charset': 'utf8mb4'
}

def connect_to_db():
    """连接到MySQL数据库"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        logger.info("数据库连接成功")
        return connection
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise

def create_province_traffic_table(connection):
    """创建province_traffic表"""
    try:
        with connection.cursor() as cursor:
            # 如果表已存在，先删除
            cursor.execute("DROP TABLE IF EXISTS province_traffic")
            
            # 创建新表
            create_table_sql = """
            CREATE TABLE province_traffic (
                id INT AUTO_INCREMENT PRIMARY KEY,
                province VARCHAR(50) NOT NULL COMMENT '省份名称',
                transport_frequency TEXT COMMENT '省份使用的交通类型及词频',
                transport_count INT COMMENT '省份的交通类型数量'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_table_sql)
            connection.commit()
            logger.info("province_traffic表创建成功")
    except Exception as e:
        logger.error(f"创建表失败: {e}")
        connection.rollback()
        raise

def create_traffic_add_table(connection):
    """创建traffic_add表"""
    try:
        with connection.cursor() as cursor:
            # 如果表已存在，先删除
            cursor.execute("DROP TABLE IF EXISTS traffic_add")
            
            # 创建新表
            create_table_sql = """
            CREATE TABLE traffic_add (
                id INT AUTO_INCREMENT PRIMARY KEY,
                transport_mode VARCHAR(50) NOT NULL COMMENT '交通方式',
                transport_count INT COMMENT '交通方式数量'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_table_sql)
            connection.commit()
            logger.info("traffic_add表创建成功")
    except Exception as e:
        logger.error(f"创建traffic_add表失败: {e}")
        connection.rollback()
        raise

def get_province_transport_data(connection):
    """从transport_mode表获取数据并按省份分组处理"""
    try:
        with connection.cursor() as cursor:
            # 查询所有数据
            query = """
            SELECT city_name, transport_mode 
            FROM transport_mode 
            WHERE city_name IS NOT NULL AND transport_mode IS NOT NULL
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            # 按省份分组数据
            province_data = {}
            for row in results:
                province = row[0]
                transport_modes = row[1].split(',') if row[1] else []
                
                if province not in province_data:
                    province_data[province] = []
                
                province_data[province].extend(transport_modes)
            
            return province_data
    except Exception as e:
        logger.error(f"获取数据失败: {e}")
        raise

def get_all_transport_modes(connection):
    """从transport_mode表获取所有交通方式数据"""
    try:
        with connection.cursor() as cursor:
            # 查询所有数据
            query = """
            SELECT transport_mode 
            FROM transport_mode 
            WHERE transport_mode IS NOT NULL
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            # 获取所有交通方式
            all_transport_modes = []
            for row in results:
                transport_modes = row[0].split(',') if row[0] else []
                all_transport_modes.extend(transport_modes)
            
            return all_transport_modes
    except Exception as e:
        logger.error(f"获取交通方式数据失败: {e}")
        raise

def process_and_insert_data(connection, province_data):
    """处理数据并插入到province_traffic表"""
    try:
        with connection.cursor() as cursor:
            for province, transport_modes in province_data.items():
                # 计算各交通工具的词频
                counter = Counter(transport_modes)
                
                # 格式化交通工具词频为"客车:20,公交:65"格式
                transport_frequency = ','.join([f"{mode}:{count}" for mode, count in counter.items()])
                
                # 计算交通工具去重后的数量
                transport_count = len(counter)
                
                # 插入数据
                insert_sql = """
                INSERT INTO province_traffic (province, transport_frequency, transport_count)
                VALUES (%s, %s, %s)
                """
                cursor.execute(insert_sql, (province, transport_frequency, transport_count))
            
            connection.commit()
            logger.info("数据处理并插入成功")
    except Exception as e:
        logger.error(f"插入数据失败: {e}")
        connection.rollback()
        raise

def process_and_insert_traffic_data(connection, all_transport_modes):
    """处理交通方式数据并插入到traffic_add表"""
    try:
        with connection.cursor() as cursor:
            # 计算各交通工具的出现次数
            counter = Counter(all_transport_modes)
            
            # 插入数据
            for transport_mode, count in counter.items():
                insert_sql = """
                INSERT INTO traffic_add (transport_mode, transport_count)
                VALUES (%s, %s)
                """
                cursor.execute(insert_sql, (transport_mode, count))
            
            connection.commit()
            logger.info("交通方式数据处理并插入成功")
    except Exception as e:
        logger.error(f"插入交通方式数据失败: {e}")
        connection.rollback()
        raise

def main():
    """主函数"""
    try:
        # 连接数据库
        connection = connect_to_db()
        
        # 创建province_traffic表
        create_province_traffic_table(connection)
        
        # 创建traffic_add表
        create_traffic_add_table(connection)
        
        # 获取数据
        province_data = get_province_transport_data(connection)
        all_transport_modes = get_all_transport_modes(connection)
        
        # 处理并插入province_traffic数据
        process_and_insert_data(connection, province_data)
        
        # 处理并插入traffic_add数据
        process_and_insert_traffic_data(connection, all_transport_modes)
        
        logger.info("所有任务完成")
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
    finally:
        # 关闭数据库连接
        if 'connection' in locals() and connection:
            connection.close()
            logger.info("数据库连接已关闭")

if __name__ == "__main__":
    main()
