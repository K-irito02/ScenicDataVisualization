import pymongo
import mysql.connector
import re
import cpca
import pandas as pd
from typing import Dict, Optional

# MongoDB连接配置
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "scenic_area"
MONGO_COLLECTION = "china_attractions_copy"

# MySQL连接配置
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "3143285505",
    "database": "scenic_area"
}

def connect_mongo():
    """连接MongoDB数据库"""
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    return db[MONGO_COLLECTION]

def connect_mysql():
    """连接MySQL数据库"""
    return mysql.connector.connect(**MYSQL_CONFIG)

def parse_location(location: str) -> Dict[str, str]:
    """
    使用cpca库解析位置信息，提取省份、城市、区县等信息
    """
    result = {
        "province": "",
        "city": "",
        "district": "",
        "street": "",
        "detail_address": location
    }
    
    if not location:
        return result
    
    # 使用cpca库解析地址
    try:
        df = cpca.transform([location])
        
        # 提取解析结果
        if not df.empty:
            province = df.iloc[0]['省']
            city = df.iloc[0]['市']
            district = df.iloc[0]['区']
            
            if province and not pd.isna(province):
                result["province"] = province
            if city and not pd.isna(city):
                result["city"] = city
            if district and not pd.isna(district):
                result["district"] = district
                
            # 提取街道信息（cpca库不直接提供街道信息，需要额外处理）
            if result["province"] and result["city"] and result["district"]:
                # 移除已识别的省市区信息，剩余部分可能包含街道
                remaining = location
                for part in [result["province"], result["city"], result["district"]]:
                    remaining = remaining.replace(part, "")
                
                # 使用正则表达式提取街道信息
                street_pattern = r"(.+?(?:街道|镇|乡))"
                street_match = re.search(street_pattern, remaining)
                if street_match:
                    result["street"] = street_match.group(1)
    except Exception as e:
        print(f"解析地址时出错: {location}, 错误: {str(e)}")
    
    return result

def process_and_save_data():
    """处理数据并保存到MySQL"""
    mongo_collection = connect_mongo()
    mysql_conn = connect_mysql()
    cursor = mysql_conn.cursor()
    
    # 创建景区表（如果不存在）
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS scenic_spots (
        id INT PRIMARY KEY AUTO_INCREMENT,
        scenic_name VARCHAR(255),
        province VARCHAR(50) NOT NULL,
        city VARCHAR(50) NOT NULL,
        district VARCHAR(50),
        street VARCHAR(100),
        detail_address VARCHAR(255)
    )
    """
    cursor.execute(create_table_sql)
    
    # 创建分析表（如果不存在）
    create_analysis_table_sql = """
    CREATE TABLE IF NOT EXISTS scenic_spots_analysis (
        id INT PRIMARY KEY AUTO_INCREMENT,
        scenic_name VARCHAR(255),
        detail_address VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_analysis_table_sql)
    
    # 获取所有景点数据
    for doc in mongo_collection.find():
        location = doc.get("location", "")
        scenic_name = doc.get("name", "")
        
        if not location:
            continue
            
        # 解析位置信息
        location_info = parse_location(location)
        
        # 如果没有解析出省份，保存到分析表
        if not location_info["province"]:
            insert_analysis_sql = """
            INSERT INTO scenic_spots_analysis 
            (scenic_name, detail_address)
            VALUES (%s, %s)
            """
            cursor.execute(insert_analysis_sql, (scenic_name, location))
            continue
        
        # 插入数据到主表
        insert_sql = """
        INSERT INTO scenic_spots 
        (scenic_name, province, city, district, street, detail_address)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            scenic_name,
            location_info["province"],
            location_info["city"],
            location_info["district"],
            location_info["street"],
            location_info["detail_address"]
        )
        
        cursor.execute(insert_sql, values)
    
    mysql_conn.commit()
    cursor.close()
    mysql_conn.close()

if __name__ == "__main__":
    process_and_save_data()
