import pymongo
import mysql.connector
from statistics import mean, median
import re

# MongoDB连接
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["scenic_area"]
attractions_collection = mongo_db["china_attractions_copy"]

# MySQL连接
mysql_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="3143285505",
    database="scenic_area"
)
mysql_cursor = mysql_conn.cursor()

# 创建hierarchy_TicketAnalysis数据库
mysql_cursor.execute("CREATE DATABASE IF NOT EXISTS hierarchy_TicketAnalysis")
mysql_cursor.execute("USE hierarchy_TicketAnalysis")

# 定义各个等级类型及其对应的字段名
level_mappings = {
    "scenic_level": {
        "field": "deep_scenic_level",
        "levels": ["5A", "4A", "省级", "3A", "2A"],
        "table_name": "scenic_level_price"
    },
    "museum_level": {
        "field": "deep_museum_level",
        "levels": ["非国有", "市级", "国家二级博物馆", "省级", "国家级", "国家一级博物馆"],
        "table_name": "museum_level_price"
    },
    "geological_park_level": {
        "field": "deep_geological_park_level",
        "levels": ["省级", "世界级", "国家级"],
        "table_name": "geological_park_level_price"
    },
    "forest_park_level": {
        "field": "deep_forest_park_level",
        "levels": ["国家级", "市级", "省级"],
        "table_name": "forest_park_level_price"
    },
    "wetland_level": {
        "field": "deep_wetland_level",
        "levels": ["国家级", "国际级", "市级"],
        "table_name": "wetland_level_price"
    },
    "cultural_relic_level": {
        "field": "deep_cultural_relic_protection_unit",
        "levels": ["国家级", "北京市文物保护单位", "市级", "省级", "上海市文物保护单位"],
        "table_name": "cultural_relic_level_price"
    },
    "nature_reserve_level": {
        "field": "deep_nature_reserve_level",
        "levels": ["国家级", "省级"],
        "table_name": "nature_reserve_level_price"
    }
}

# 获取价格数据
mysql_cursor.execute("SELECT scenic_name, ticket FROM scenic_area.price_process")
price_data = {row[0]: row[1] for row in mysql_cursor.fetchall()}

def process_ticket_price(ticket_str):
    if not ticket_str or ticket_str == "免费":
        return None
    prices = [float(p) for p in re.findall(r'\d+', ticket_str)]
    # 过滤掉小于4元的票价
    prices = [p for p in prices if p > 4]
    return prices if prices else None

def create_and_populate_tables():
    for category, info in level_mappings.items():
        # 创建表
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {info['table_name']} (
            level VARCHAR(50) PRIMARY KEY,
            count INT,
            average_price DECIMAL(10, 2),
            min_price DECIMAL(10, 2),
            max_price DECIMAL(10, 2),
            median_price DECIMAL(10, 2)
        )
        """
        mysql_cursor.execute(create_table_sql)
        
        # 处理每个等级
        for level in info['levels']:
            # 获取该等级的所有景区
            attractions = attractions_collection.find({info['field']: level})
            
            # 统计数量和价格
            count = 0
            all_prices = []
            
            for attraction in attractions:
                count += 1
                name = attraction.get('name')
                if name in price_data:
                    prices = process_ticket_price(price_data[name])
                    if prices:
                        all_prices.extend(prices)
            
            # 计算价格统计数据
            if all_prices:
                # 确保所有价格都大于0
                non_zero_prices = [p for p in all_prices if p > 0]
                
                if non_zero_prices:
                    avg_price = mean(all_prices)
                    min_price = min(non_zero_prices)  # 使用非零价格计算最小值
                    max_price = max(all_prices)
                    median_price = median(all_prices)
                else:
                    avg_price = None
                    min_price = None
                    max_price = None
                    median_price = None
            else:
                avg_price = None
                min_price = None
                max_price = None
                median_price = None
            
            # 插入数据
            insert_sql = f"""
            INSERT INTO {info['table_name']} 
            (level, count, average_price, min_price, max_price, median_price)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            mysql_cursor.execute(insert_sql, (level, count, avg_price, min_price, max_price, median_price))
            
        mysql_conn.commit()

if __name__ == "__main__":
    create_and_populate_tables()
    mysql_cursor.close()
    mysql_conn.close()
    mongo_client.close()
