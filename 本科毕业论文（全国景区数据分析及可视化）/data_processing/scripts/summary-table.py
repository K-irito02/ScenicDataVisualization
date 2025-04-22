#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
import pymysql
import re
import logging
from pymongo.collection import Collection
from typing import Dict, List, Any, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库配置
MONGO_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'db': 'scenic_area',
    'collection': 'china_attractions_copy'
}

MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '3143285505',  # 请修改为实际密码
    'database': 'scenic_area',
    'charset': 'utf8mb4'
}

def connect_mongo() -> Tuple[pymongo.MongoClient, Collection]:
    """连接MongoDB数据库"""
    try:
        client = pymongo.MongoClient(
            host=MONGO_CONFIG['host'],
            port=MONGO_CONFIG['port']
        )
        db = client[MONGO_CONFIG['db']]
        collection = db[MONGO_CONFIG['collection']]
        logger.info(f"成功连接MongoDB: {MONGO_CONFIG['db']}.{MONGO_CONFIG['collection']}")
        return client, collection
    except Exception as e:
        logger.error(f"MongoDB连接失败: {str(e)}")
        raise

def connect_mysql() -> pymysql.connections.Connection:
    """连接MySQL数据库"""
    try:
        connection = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'],
            charset=MYSQL_CONFIG['charset']
        )
        logger.info(f"成功连接MySQL: {MYSQL_CONFIG['database']}")
        return connection
    except Exception as e:
        logger.error(f"MySQL连接失败: {str(e)}")
        raise

def get_scenic_spots_from_mysql(connection: pymysql.connections.Connection) -> Dict[str, Dict]:
    """从MySQL的scenic_spots表获取景区地理位置信息"""
    result = {}
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT scenic_name, province, city, district, street FROM scenic_spots"
            cursor.execute(sql)
            for row in cursor.fetchall():
                result[row['scenic_name']] = row
        logger.info(f"从scenic_spots表获取了{len(result)}条景区数据")
        return result
    except Exception as e:
        logger.error(f"获取scenic_spots数据失败: {str(e)}")
        return {}

def get_price_data_from_mysql(connection: pymysql.connections.Connection) -> Dict[str, str]:
    """从MySQL的price_process表获取景区票价信息"""
    result = {}
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT scenic_name, ticket FROM price_process"
            cursor.execute(sql)
            for row in cursor.fetchall():
                result[row['scenic_name']] = row['ticket']
        logger.info(f"从price_process表获取了{len(result)}条票价数据")
        return result
    except Exception as e:
        logger.error(f"获取price_process数据失败: {str(e)}")
        return {}

def get_transport_data_from_mysql(connection: pymysql.connections.Connection) -> Dict[str, str]:
    """从MySQL的transport_mode表获取景区交通方式信息"""
    result = {}
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT scenic_name, transport_mode FROM transport_mode"
            cursor.execute(sql)
            for row in cursor.fetchall():
                result[row['scenic_name']] = row['transport_mode']
        logger.info(f"从transport_mode表获取了{len(result)}条交通方式数据")
        return result
    except Exception as e:
        logger.error(f"获取transport_mode数据失败: {str(e)}")
        return {}

def get_sentiment_data_from_mysql(connection: pymysql.connections.Connection) -> Dict[str, Dict]:
    """从MySQL获取情感分析相关数据"""
    result = {}
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT name, emo_tend, emo_score, emo_inten, highFre_words FROM comment_handling"
            cursor.execute(sql)
            for row in cursor.fetchall():
                result[row['name']] = row
        logger.info(f"从comment_handling表获取了{len(result)}条情感分析数据")
        return result
    except Exception as e:
        logger.error(f"获取情感分析数据失败: {str(e)}")
        return {}

def extract_minimum_price(price_str: str) -> str:
    """从票价字符串中提取最低票价"""
    if not price_str or price_str == "免费":
        return "免费"
    
    # 尝试提取数字
    numbers = re.findall(r'\d+', price_str)
    if numbers:
        return min([int(num) for num in numbers])
    
    return "请咨询景区"

def format_scenic_level(doc: Dict[str, Any]) -> str:
    """格式化景区类型及级别信息"""
    level_parts = []
    
    if doc.get("deep_scenic_level"):
        level_parts.append(f"{doc['deep_scenic_level']}景区")
    
    if doc.get("deep_forest_park_level"):
        level_parts.append(f"森林公园:{doc['deep_forest_park_level']}")
    
    if doc.get("deep_geological_park_level"):
        level_parts.append(f"地质公园:{doc['deep_geological_park_level']}")
    
    if doc.get("deep_nature_reserve_level"):
        level_parts.append(f"自然保护区:{doc['deep_nature_reserve_level']}")
    
    if doc.get("deep_cultural_relic_protection_unit"):
        level_parts.append(f"文物保护单位:{doc['deep_cultural_relic_protection_unit']}")
    
    if doc.get("deep_museum_level"):
        level_parts.append(f"博物馆:{doc['deep_museum_level']}")
    
    if doc.get("deep_water_conservancy_scenic_area") == "是":
        level_parts.append("水利风景区")
    
    if doc.get("deep_wetland_level"):
        level_parts.append(f"湿地风景区:{doc['deep_wetland_level']}")
    
    return ", ".join(level_parts) if level_parts else ""

def create_or_update_summary_table(connection: pymysql.connections.Connection) -> None:
    """创建或更新summary-table表"""
    try:
        with connection.cursor() as cursor:
            # 检查表是否存在
            cursor.execute("SHOW TABLES LIKE 'summary_table'")
            table_exists = cursor.fetchone()
            
            # 如果表不存在，创建表
            if not table_exists:
                sql = """
                CREATE TABLE `summary_table` (
                  `景区ID` INT AUTO_INCREMENT PRIMARY KEY,
                  `景区名称` VARCHAR(255) NOT NULL,
                  `图片URL` TEXT,
                  `景区简介` TEXT,
                  `所在省份` VARCHAR(50),
                  `所在城市` VARCHAR(50),
                  `所在区县` VARCHAR(50),
                  `所在街道镇乡` VARCHAR(100),
                  `经纬度` VARCHAR(50),
                  `地址原数据` VARCHAR(255),
                  `景区类型及级别` VARCHAR(255),
                  `开放时间原数据` TEXT,
                  `票价原数据` TEXT,
                  `交通原数据` TEXT,
                  `评论原数据` LONGTEXT,
                  `最低票价` VARCHAR(50),
                  `交通方式` VARCHAR(255),
                  `评论数量` INT,
                  `情感倾向` VARCHAR(10),
                  `情感得分` FLOAT,
                  `情感强度` FLOAT,
                  `高频词` TEXT,
                  `更新时间` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                  INDEX `idx_景区名称` (`景区名称`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
                cursor.execute(sql)
                connection.commit()
                logger.info("成功创建summary_table表")
            else:
                # 如果表已存在，检查并修改评论原数据字段类型
                cursor.execute("DESCRIBE summary_table `评论原数据`")
                field_info = cursor.fetchone()
                if field_info and field_info[1].upper() != 'LONGTEXT':
                    cursor.execute("ALTER TABLE summary_table MODIFY COLUMN `评论原数据` LONGTEXT")
                    connection.commit()
                    logger.info("已修改评论原数据字段类型为LONGTEXT")
    except Exception as e:
        logger.error(f"创建或更新summary_table表失败: {str(e)}")
        raise

def process_and_insert_data(
    mongo_collection: Collection,
    mysql_connection: pymysql.connections.Connection,
    scenic_spots_data: Dict[str, Dict],
    price_data: Dict[str, str],
    transport_data: Dict[str, str],
    sentiment_data: Dict[str, Dict]
) -> None:
    """处理MongoDB数据并插入到MySQL的summary_table表"""
    try:
        cursor = mysql_connection.cursor()
        
        # 获取MongoDB中的所有景区数据
        mongo_docs = list(mongo_collection.find({}))
        logger.info(f"从MongoDB获取了{len(mongo_docs)}条景区数据")
        
        # 清空现有表数据
        cursor.execute("TRUNCATE TABLE summary_table")
        
        # 批量插入数据
        insert_count = 0
        for doc in mongo_docs:
            scenic_name = doc.get("name", "")
            if not scenic_name:
                continue
            
            # 获取地理位置数据
            location_data = scenic_spots_data.get(scenic_name, {})
            
            # 获取票价数据
            lowest_price = "请咨询景区"
            if scenic_name in price_data:
                lowest_price = extract_minimum_price(price_data[scenic_name])
            
            # 获取交通方式
            transport_mode = "具体交通详情如下"
            if scenic_name in transport_data:
                transport_mode = transport_data[scenic_name]
            
            # 获取情感分析数据
            sentiment = sentiment_data.get(scenic_name, {})
            
            # 处理经纬度 - 增强空值处理
            coordinates = doc.get("deep_coordinates", [])
            if coordinates is None:
                coordinates = []
            coordinates_str = ""
            if len(coordinates) >= 2:
                coordinates_str = f"{coordinates[0]},{coordinates[1]}"
            
            # 处理评论原数据 - 获取全部评论，增强空值处理
            comments = doc.get("comments", [])
            if comments is None:
                comments = []
            comments_str = "\n".join(comments) if comments else ""
            
            # 处理开放时间
            opening_hours = doc.get("opening_hours")
            if not opening_hours:
                opening_hours = doc.get("deep_opening_hours", "")
            
            # 处理票价原数据
            ticket = doc.get("ticket")
            if isinstance(ticket, list):
                ticket_str = "\n".join(ticket)
            elif ticket is None:
                ticket_str = ""
            else:
                ticket_str = str(ticket) if ticket else ""
            
            if not ticket_str:
                ticket_str = doc.get("deep_ticket_price", "")
            
            # 格式化景区类型及级别
            scenic_level = format_scenic_level(doc)
            
            # 插入数据
            sql = """
            INSERT INTO summary_table (
                `景区名称`, `图片URL`, `景区简介`, `所在省份`, `所在城市`, `所在区县`, 
                `所在街道镇乡`, `经纬度`, `地址原数据`, `景区类型及级别`, `开放时间原数据`, 
                `票价原数据`, `交通原数据`, `评论原数据`, `最低票价`, `交通方式`, 
                `评论数量`, `情感倾向`, `情感得分`, `情感强度`, `高频词`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                scenic_name,
                doc.get("image", ""),
                doc.get("summary", ""),
                location_data.get("province", ""),
                location_data.get("city", ""),
                location_data.get("district", ""),
                location_data.get("street", ""),
                coordinates_str,
                doc.get("location", ""),
                scenic_level,
                opening_hours,
                ticket_str,
                doc.get("transport", ""),
                comments_str,
                lowest_price,
                transport_mode,
                doc.get("comment_count", 0),
                sentiment.get("emo_tend", ""),
                sentiment.get("emo_score", 0.0),
                sentiment.get("emo_inten", 0.0),
                sentiment.get("highFre_words", "")
            )
            
            try:
                cursor.execute(sql, values)
                insert_count += 1
                
                # 每500条提交一次
                if insert_count % 500 == 0:
                    mysql_connection.commit()
                    logger.info(f"已处理{insert_count}条数据")
            except pymysql.err.DataError as e:
                logger.warning(f"插入景区 {scenic_name} 数据失败: {str(e)}，跳过此记录")
                continue
            except Exception as e:
                logger.warning(f"插入景区 {scenic_name} 数据时出现未知错误: {str(e)}，跳过此记录")
                continue
        
        # 提交剩余事务
        mysql_connection.commit()
        logger.info(f"数据处理完成，共插入{insert_count}条数据")
    
    except Exception as e:
        mysql_connection.rollback()
        logger.error(f"数据处理失败: {str(e)}")
        raise
    finally:
        cursor.close()

def main():
    """主函数"""
    mongo_client = None
    mysql_conn = None
    
    try:
        # 连接数据库
        mongo_client, mongo_collection = connect_mongo()
        mysql_conn = connect_mysql()
        
        # 创建或更新表结构
        create_or_update_summary_table(mysql_conn)
        
        # 获取MySQL中的辅助数据
        scenic_spots_data = get_scenic_spots_from_mysql(mysql_conn)
        price_data = get_price_data_from_mysql(mysql_conn)
        transport_data = get_transport_data_from_mysql(mysql_conn)
        sentiment_data = get_sentiment_data_from_mysql(mysql_conn)
        
        # 处理数据并插入到summary_table
        process_and_insert_data(
            mongo_collection,
            mysql_conn,
            scenic_spots_data,
            price_data,
            transport_data,
            sentiment_data
        )
        
        logger.info("数据汇总脚本执行完成")
    
    except Exception as e:
        logger.error(f"脚本执行失败: {str(e)}")
    
    finally:
        # 关闭数据库连接
        if mongo_client:
            mongo_client.close()
        if mysql_conn:
            mysql_conn.close()

if __name__ == "__main__":
    main()
