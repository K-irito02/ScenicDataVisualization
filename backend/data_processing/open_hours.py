#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
景区开放时间数据清理及预处理模块
处理MongoDB的开放时间数据并将结构化后的数据存入MySQL
"""

import re
import pymongo
import mysql.connector
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("open_hours_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("open_hours_processor")

class OpenHoursProcessor:
    """景区开放时间数据处理类"""
    
    def __init__(self, mongo_config, mysql_config):
        """
        初始化数据库连接
        
        Args:
            mongo_config: MongoDB连接配置
            mysql_config: MySQL连接配置
        """
        # 连接到MongoDB
        self.mongo_client = pymongo.MongoClient(**mongo_config)
        self.mongo_db = self.mongo_client["scenic_area"]
        self.mongo_collection = self.mongo_db["china_attractions_copy"]
        
        # 连接到MySQL
        self.mysql_conn = mysql.connector.connect(**mysql_config)
        self.mysql_cursor = self.mysql_conn.cursor()
        
        # 创建MySQL表（如果不存在）
        self._create_tables()
    
    def _create_tables(self):
        """创建MySQL表结构"""
        # 创建time_process表，用于存储处理后的开放时间数据
        self.mysql_cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_process (
            id INT AUTO_INCREMENT PRIMARY KEY,
            scenic_name VARCHAR(255),  # 景区名称
            city_name VARCHAR(255),   # 城市名称
            time_range TEXT,          # 开放时间段
            date_range TEXT,          # 日期范围
            weekdays TEXT,            # 适用星期
            season VARCHAR(50),       # 季节
            is_holiday BOOLEAN,       # 是否节假日
            is_closed BOOLEAN,        # 是否闭馆
            is_24h BOOLEAN,           # 是否全天开放
            stop_ticket_time VARCHAR(50)  # 停止售票时间
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        # 创建time_analysis表，用于存储无法处理的数据以便后续分析
        self.mysql_cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_analysis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            scenic_name VARCHAR(255),  # 景区名称
            city_name VARCHAR(255),   # 城市名称
            opening_hours TEXT        # 原始开放时间数据
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        
        self.mysql_conn.commit()
    
    def process_all_data(self):
        """处理所有景区数据"""
        count = 0  # 处理的记录计数
        total = self.mongo_collection.count_documents({})  # 总记录数
        logger.info(f"开始处理共 {total} 条景区数据")
        
        for record in self.mongo_collection.find():
            count += 1
            if count % 100 == 0:
                logger.info(f"已处理 {count}/{total} 条数据")
                
            scenic_name = record.get("name", "")  # 获取景区名称
            city_name = record.get("city", "")  # 获取城市名称
            
            # 优先使用opening_hours字段，如果为空则使用deep_opening_hours
            opening_hours = record.get("opening_hours")
            if not opening_hours:
                opening_hours = record.get("deep_opening_hours")
            
            if not opening_hours:
                continue  # 跳过没有开放时间数据的记录
            
            try:
                processed_data = self.process_opening_hours(opening_hours)
                
                # 如果处理成功，将数据插入time_process表
                if processed_data.get("time_range"):
                    self._insert_to_time_process(scenic_name, city_name, processed_data)
                else:
                    # 如果处理失败，将原始数据插入time_analysis表以便后续调试
                    self._insert_to_time_analysis(scenic_name, city_name, opening_hours)
            except Exception as e:
                logger.error(f"处理记录时出错: {e}, 景区: {scenic_name}, 开放时间: {opening_hours}")
                # 将出错的数据插入time_analysis表以便后续分析
                self._insert_to_time_analysis(scenic_name, city_name, opening_hours)
        
        logger.info(f"数据处理完成，共处理 {count} 条数据")
    
    def process_opening_hours(self, opening_hours_str):
        """
        处理开放时间字符串
        
        Args:
            opening_hours_str: 开放时间原始字符串
        
        Returns:
            dict: 处理后的结构化数据
        """
        # 初始化结果字典
        result = {
            "time_range": "",  # 开放时间段
            "date_range": "",  # 日期范围
            "weekdays": "",    # 适用星期
            "season": "",      # 季节
            "is_holiday": False, # 是否节假日
            "is_closed": False,  # 是否闭馆
            "is_24h": False,     # 是否全天开放
            "stop_ticket_time": ""  # 停止售票时间
        }
        
        if not opening_hours_str:
            return result
        
        try:
            # 确保opening_hours_str是字符串
            opening_hours_str = str(opening_hours_str)
            
            # 清理字符串，去除换行符
            opening_hours_str = opening_hours_str.replace("\n", " ").strip()
            
            # 检查是否全天开放
            if "全天" in opening_hours_str:
                result["is_24h"] = True
                result["time_range"] = "00:00-24:00"
            
            # 检查是否闭馆
            if "不对外开放" in opening_hours_str or "停止营业" in opening_hours_str or "全天不开放" in opening_hours_str:
                result["is_closed"] = True
            
            # 提取时间段 - 增强版
            time_ranges = []
            
            # 处理标准时间格式 08:00-17:00
            standard_time_pattern = r'(\d{1,2}[:：]\d{1,2})-(\d{1,2}[:：]\d{1,2}|次日\d{1,2}[:：]\d{1,2})'
            standard_time_matches = re.finditer(standard_time_pattern, opening_hours_str)
            
            for match in standard_time_matches:
                start_time, end_time = match.groups()
                
                # 标准化时间格式
                start_time = start_time.replace("：", ":")
                end_time = end_time.replace("：", ":")
                
                # 处理次日情况
                if "次日" in end_time:
                    end_time = end_time.replace("次日", "")
                    # 如果结束时间包含"次日"，需要特殊处理
                    if end_time == "00:00":
                        end_time = "24:00"  # 转换为24小时制表示午夜
                
                time_range = f"{start_time}-{end_time}"
                if time_range not in time_ranges:
                    time_ranges.append(time_range)
            
            # 处理带有am/pm的时间格式 08:00am－6:00pm
            ampm_pattern = r'(\d{1,2}[:：]?\d{0,2})(?:am|AM|上午)?[－-](\d{1,2}[:：]?\d{0,2})(?:pm|PM|下午)?'
            ampm_matches = re.finditer(ampm_pattern, opening_hours_str)
            
            for match in ampm_matches:
                start_time, end_time = match.groups()
                
                # 标准化时间格式
                start_time = self._normalize_time(start_time, "am" in match.group().lower() or "上午" in match.group())
                end_time = self._normalize_time(end_time, "pm" in match.group().lower() or "下午" in match.group())
                
                time_range = f"{start_time}-{end_time}"
                if time_range not in time_ranges and "-" in time_range:  # 确保是有效的时间范围
                    time_ranges.append(time_range)
            
            # 处理使用"至"或"到"连接的时间格式 9:00至17:00
            to_pattern = r'(\d{1,2}[:：]\d{1,2})\s*[至到]\s*(\d{1,2}[:：]\d{1,2})'
            to_matches = re.finditer(to_pattern, opening_hours_str)
            
            for match in to_matches:
                start_time, end_time = match.groups()
                
                # 标准化时间格式
                start_time = start_time.replace("：", ":")
                end_time = end_time.replace("：", ":")
                
                time_range = f"{start_time}-{end_time}"
                if time_range not in time_ranges:
                    time_ranges.append(time_range)
            
            # 处理单个时间点 08:00
            single_time_pattern = r'(?<![0-9:-])(\d{1,2}[:：]\d{1,2})(?![0-9:-])'
            single_time_matches = re.findall(single_time_pattern, opening_hours_str)
            
            for time_str in single_time_matches:
                normalized_time = time_str.replace("：", ":")
                # 安全地检查是否已存在
                try:
                    if all(normalized_time != t.split("-")[0] for t in time_ranges if "-" in t) and \
                       all(normalized_time != t.split("-")[1] for t in time_ranges if "-" in t) and \
                       normalized_time not in time_ranges:
                        time_ranges.append(normalized_time)
                except Exception:
                    # 如果出现任何错误，直接添加
                    if normalized_time not in time_ranges:
                        time_ranges.append(normalized_time)
            
            # 处理特殊格式：周一至周五：下午14:00—17:00； 晚上19:00—23:00
            special_pattern = r'(上午|下午|晚上)?(\d{1,2}[:：]?\d{0,2})[—－-](上午|下午|晚上)?(\d{1,2}[:：]?\d{0,2})'
            special_matches = re.finditer(special_pattern, opening_hours_str)
            
            for match in special_matches:
                prefix1, start_time, prefix2, end_time = match.groups()
                
                # 标准化时间格式
                start_time = self._normalize_time(start_time, prefix1 == "下午" or prefix1 == "晚上")
                end_time = self._normalize_time(end_time, prefix2 == "下午" or prefix2 == "晚上")
                
                time_range = f"{start_time}-{end_time}"
                if time_range not in time_ranges and "-" in time_range:
                    time_ranges.append(time_range)
            
            # 处理表演时间等特殊情况
            if "表演" in opening_hours_str or "开演" in opening_hours_str:
                performance_pattern = r'(\d{1,2}[:：]\d{1,2})'
                performance_times = re.findall(performance_pattern, opening_hours_str)
                
                for time_str in performance_times:
                    normalized_time = time_str.replace("：", ":")
                    if normalized_time not in time_ranges:
                        time_ranges.append(normalized_time)
            
            if time_ranges:
                result["time_range"] = ",".join(time_ranges)
            
            # 提取日期范围
            date_ranges = []
            date_pattern = r'(\d{1,2}月\d{1,2}日|\d{2}月\d{2}日)-(\d{1,2}月\d{1,2}日|次年\d{1,2}月\d{1,2}日|\d{2}月\d{2}日)'
            date_matches = re.finditer(date_pattern, opening_hours_str)
            
            for match in date_matches:
                start_date, end_date = match.groups()
                date_range = f"{start_date}-{end_date}"
                if date_range not in date_ranges:
                    date_ranges.append(date_range)
            
            if date_ranges:
                result["date_range"] = ",".join(date_ranges)
            
            # 提取星期信息 - 增强版
            weekdays = []
            
            # 标准格式：周一-周日
            std_weekdays_pattern = r'(周[一二三四五六日]|周一-周[日五六七]|周[一二三四五六]-周日)'
            std_weekdays_matches = re.findall(std_weekdays_pattern, opening_hours_str)
            
            if std_weekdays_matches:
                for weekday in std_weekdays_matches:
                    if weekday not in weekdays:
                        weekdays.append(weekday)
            
            # 处理"周一至周日"格式
            zh_weekdays_pattern = r'(周[一二三四五六日])至(周[一二三四五六日])'
            zh_weekdays_matches = re.findall(zh_weekdays_pattern, opening_hours_str)
            
            if zh_weekdays_matches:
                for start_day, end_day in zh_weekdays_matches:
                    weekday_range = f"{start_day}-{end_day}"
                    if weekday_range not in weekdays:
                        weekdays.append(weekday_range)
            
            # 处理"周日 - 周六"格式
            dash_weekdays_pattern = r'(周[一二三四五六日])\s*[-－]\s*(周[一二三四五六日])'
            dash_weekdays_matches = re.findall(dash_weekdays_pattern, opening_hours_str)
            
            if dash_weekdays_matches:
                for start_day, end_day in dash_weekdays_matches:
                    weekday_range = f"{start_day}-{end_day}"
                    if weekday_range not in weekdays:
                        weekdays.append(weekday_range)
            
            # 处理"周六、周日"格式
            comma_weekdays_pattern = r'(周[一二三四五六日])、(周[一二三四五六日])'
            comma_weekdays_matches = re.findall(comma_weekdays_pattern, opening_hours_str)
            
            if comma_weekdays_matches:
                for day1, day2 in comma_weekdays_matches:
                    if day1 not in weekdays:
                        weekdays.append(day1)
                    if day2 not in weekdays:
                        weekdays.append(day2)
            
            if weekdays:
                result["weekdays"] = ",".join(weekdays)
            
            # 提取季节信息
            seasons = []
            if "春季" in opening_hours_str:
                seasons.append("春季")
            if "夏季" in opening_hours_str:
                seasons.append("夏季")
            if "秋季" in opening_hours_str:
                seasons.append("秋季")
            if "冬季" in opening_hours_str:
                seasons.append("冬季")
            
            if seasons:
                result["season"] = ",".join(seasons)
            
            # 检查是否节假日相关
            if "节假日" in opening_hours_str or "劳动节" in opening_hours_str or "端午节" in opening_hours_str:
                result["is_holiday"] = True
            
            # 提取停止售票时间
            stop_ticket_pattern = r'停止售票时间[:：](\d{1,2}[:：]\d{1,2})'
            stop_ticket_match = re.search(stop_ticket_pattern, opening_hours_str)
            
            if stop_ticket_match:
                result["stop_ticket_time"] = stop_ticket_match.group(1).replace("：", ":")
            
            return result
        except Exception as e:
            logger.error(f"处理开放时间字符串时出错: {e}, 原始字符串: {opening_hours_str}")
            return result  # 返回空结果
    
    def _normalize_time(self, time_str, is_pm=False):
        """
        标准化时间格式
        
        Args:
            time_str: 原始时间字符串
            is_pm: 是否为下午时间
            
        Returns:
            str: 标准化后的时间字符串 (HH:MM)
        """
        try:
            # 移除所有非数字字符，保留冒号
            time_str = time_str.replace("：", ":")
            
            if ":" not in time_str:
                # 如果没有冒号，假设是小时
                hour = int(time_str)
                minute = 0
            else:
                parts = time_str.split(":")
                hour = int(parts[0])
                # 确保parts[1]不为空且只包含数字
                if len(parts) > 1 and parts[1].strip():
                    # 提取分钟部分的数字
                    minute_str = ''.join(c for c in parts[1] if c.isdigit())
                    minute = int(minute_str) if minute_str else 0
                else:
                    minute = 0
            
            # 处理下午时间
            if is_pm and hour < 12:
                hour += 12
            
            # 格式化为HH:MM
            return f"{hour:02d}:{minute:02d}"
        except Exception as e:
            logger.warning(f"时间格式化失败: {time_str}, 错误: {e}")
            return "00:00"  # 返回默认值
    
    def _insert_to_time_process(self, scenic_name, city_name, data):
        """将处理后的数据插入time_process表"""
        try:
            query = """
            INSERT INTO time_process 
            (scenic_name, city_name, time_range, date_range, weekdays, 
             season, is_holiday, is_closed, is_24h, stop_ticket_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                scenic_name, city_name, data["time_range"], data["date_range"], 
                data["weekdays"], data["season"], data["is_holiday"], 
                data["is_closed"], data["is_24h"], data["stop_ticket_time"]
            )
            
            self.mysql_cursor.execute(query, values)
            self.mysql_conn.commit()
        except Exception as e:
            logger.error(f"插入time_process表失败: {e}")
            self.mysql_conn.rollback()
    
    def _insert_to_time_analysis(self, scenic_name, city_name, opening_hours):
        """将原始数据插入time_analysis表"""
        try:
            query = """
            INSERT INTO time_analysis 
            (scenic_name, city_name, opening_hours)
            VALUES (%s, %s, %s)
            """
            values = (scenic_name, city_name, opening_hours)
            
            self.mysql_cursor.execute(query, values)
            self.mysql_conn.commit()
        except Exception as e:
            logger.error(f"插入time_analysis表失败: {e}")
            self.mysql_conn.rollback()
    
    def close(self):
        """关闭数据库连接"""
        if self.mongo_client:
            self.mongo_client.close()
        
        if self.mysql_cursor:
            self.mysql_cursor.close()
        
        if self.mysql_conn:
            self.mysql_conn.close()


def main():
    """主函数"""
    # 数据库配置
    mongo_config = {
        "host": "localhost",
        "port": 27017,
        # 根据实际情况配置用户名和密码
        # "username": "username",
        # "password": "password"
    }
    
    mysql_config = {
        "host": "localhost",
        "user": "root",
        "password": "3143285505",  # 替换为实际密码
        "database": "scenic_area"
    }
    
    try:
        processor = OpenHoursProcessor(mongo_config, mysql_config)
        processor.process_all_data()
    except Exception as e:
        logger.error(f"处理开放时间数据时发生错误: {e}")
    finally:
        if 'processor' in locals():
            processor.close()


if __name__ == "__main__":
    main()
