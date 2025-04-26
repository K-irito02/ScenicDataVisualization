#!/usr/bin/env python
"""
数据迁移脚本 - 将hierarchy_ticketanalysis数据库中的表迁移到scenic_area数据库

使用方法:
1. 确保两个数据库都存在并且可访问
2. 执行 python manage.py shell < scripts/migrate_hierarchy_tables.py
"""

import os
import sys
import django
import MySQLdb
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# 定义源数据库和目标数据库的连接参数
SOURCE_DB = {
    'name': 'hierarchy_ticketanalysis',
    'user': 'root',  # 替换为您的数据库用户名
    'password': '3143285505',  # 替换为您的数据库密码
    'host': 'localhost',
    'port': 3306
}

TARGET_DB = {
    'name': 'scenic_area',
    'user': 'root',  # 替换为您的数据库用户名
    'password': '3143285505',  # 替换为您的数据库密码
    'host': 'localhost',
    'port': 3306
}

# 要迁移的表列表
TABLES = [
    'scenic_level_price',
    'museum_level_price',
    'geological_park_level_price',
    'forest_park_level_price',
    'wetland_level_price',
    'cultural_relic_level_price',
    'nature_reserve_level_price'
]

def migrate_table(source_conn, target_conn, table_name):
    """迁移单个表的数据"""
    try:
        logger.info(f"开始迁移表 {table_name}")
        
        # 获取表结构
        source_cursor = source_conn.cursor()
        source_cursor.execute(f"SHOW CREATE TABLE {table_name}")
        create_table_stmt = source_cursor.fetchone()[1]
        
        # 在目标数据库中创建表（如果不存在）
        target_cursor = target_conn.cursor()
        try:
            target_cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            target_cursor.execute(create_table_stmt)
            logger.info(f"在目标数据库中创建表 {table_name}")
        except Exception as e:
            logger.error(f"创建表失败: {str(e)}")
            return False
        
        # 获取源数据库中的数据
        source_cursor.execute(f"SELECT * FROM {table_name}")
        rows = source_cursor.fetchall()
        if not rows:
            logger.warning(f"表 {table_name} 中没有数据")
            return True
        
        # 获取列名
        source_cursor.execute(f"DESCRIBE {table_name}")
        columns = [column[0] for column in source_cursor.fetchall()]
        
        # 在目标数据库中插入数据
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        target_cursor.executemany(insert_query, rows)
        target_conn.commit()
        
        logger.info(f"成功迁移表 {table_name}，共迁移 {len(rows)} 条数据")
        return True
    except Exception as e:
        logger.error(f"迁移表 {table_name} 失败: {str(e)}")
        return False

def main():
    """主函数，执行数据迁移"""
    logger.info("开始数据迁移")
    
    try:
        # 连接源数据库
        source_conn = MySQLdb.connect(
            host=SOURCE_DB['host'],
            user=SOURCE_DB['user'],
            passwd=SOURCE_DB['password'],
            db=SOURCE_DB['name'],
            port=SOURCE_DB['port']
        )
        logger.info("成功连接到源数据库")
        
        # 连接目标数据库
        target_conn = MySQLdb.connect(
            host=TARGET_DB['host'],
            user=TARGET_DB['user'],
            passwd=TARGET_DB['password'],
            db=TARGET_DB['name'],
            port=TARGET_DB['port']
        )
        logger.info("成功连接到目标数据库")
        
        # 迁移每个表
        success_count = 0
        for table in TABLES:
            if migrate_table(source_conn, target_conn, table):
                success_count += 1
        
        # 关闭连接
        source_conn.close()
        target_conn.close()
        
        logger.info(f"数据迁移完成，成功迁移 {success_count}/{len(TABLES)} 个表")
        
    except Exception as e:
        logger.error(f"数据迁移过程中发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 