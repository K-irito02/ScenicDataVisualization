#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
景区门票价格数据处理及结构化
从MongoDB中提取门票价格数据，进行处理并存储到MySQL中
"""

import re
import pymongo
import mysql.connector
from typing import Dict, List, Any, Optional, Tuple, Union
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ticket_prices_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 数据库配置
MONGO_CONFIG = {
    'host': 'localhost',  # MongoDB主机地址
    'port': 27017,  # MongoDB端口
    'db': 'scenic_area',  # MongoDB数据库名称
    'collection': 'china_attractions_copy'  # MongoDB集合名称
}

MYSQL_CONFIG = {
    'host': 'localhost',  # MySQL主机地址
    'user': 'root',  # MySQL用户名
    'password': '3143285505',  # MySQL密码，请根据实际情况修改
    'database': 'scenic_area'  # MySQL数据库名称
}

class TicketPriceProcessor:
    """处理景区门票价格数据的类"""
    
    def __init__(self, mongo_config: Dict[str, Any], mysql_config: Dict[str, Any]):
        """初始化数据库连接和处理器"""
        self.mongo_config = mongo_config  # MongoDB配置
        self.mysql_config = mysql_config  # MySQL配置
        self.mongo_client = None  # MongoDB客户端
        self.mysql_conn = None  # MySQL连接
        self.mysql_cursor = None  # MySQL游标
        
    def connect_databases(self):
        """连接MongoDB和MySQL数据库"""
        try:
            # 连接MongoDB
            self.mongo_client = pymongo.MongoClient(
                host=self.mongo_config['host'], 
                port=self.mongo_config['port']
            )
            mongo_db = self.mongo_client[self.mongo_config['db']]  # 获取MongoDB数据库
            self.mongo_collection = mongo_db[self.mongo_config['collection']]  # 获取MongoDB集合
            
            # 连接MySQL
            self.mysql_conn = mysql.connector.connect(**self.mysql_config)  # 建立MySQL连接
            self.mysql_cursor = self.mysql_conn.cursor()  # 创建MySQL游标
            
            # 创建MySQL表（如果不存在）
            self._create_mysql_tables()
            
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            return False
    
    def _create_mysql_tables(self):
        """创建MySQL表结构"""
        # 创建price_process表
        create_price_process_table = """
        CREATE TABLE IF NOT EXISTS price_process (
            id INT AUTO_INCREMENT PRIMARY KEY,  # 自增主键
            scenic_name VARCHAR(255) NOT NULL,  # 景区名称
            city_name VARCHAR(255),  # 城市名称
            ticket VARCHAR(1000),  # 门票信息
            full_price VARCHAR(255),  # 全价票信息
            half_price VARCHAR(255),  # 半价票信息
            adult_ticket VARCHAR(255),  # 成人票信息
            student_child_senior_ticket VARCHAR(255),  # 学生/儿童/老人票信息
            discount_ticket VARCHAR(255),  # 优惠票信息
            has_other_fees BOOLEAN DEFAULT FALSE,  # 是否有其他费用
            has_free_or_discount BOOLEAN DEFAULT FALSE,  # 是否有免票或优惠
            has_time_periods BOOLEAN DEFAULT FALSE,  # 是否分时段
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  # 创建时间
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  # 更新时间
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        
        # 创建price_analysis表
        create_price_analysis_table = """
        CREATE TABLE IF NOT EXISTS price_analysis (
            id INT AUTO_INCREMENT PRIMARY KEY,  # 自增主键
            scenic_name VARCHAR(255) NOT NULL,  # 景区名称
            city_name VARCHAR(255),  # 城市名称
            ticket_price TEXT,  # 原始票价信息
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  # 创建时间
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        
        try:
            self.mysql_cursor.execute(create_price_process_table)  # 执行创建price_process表的SQL
            self.mysql_cursor.execute(create_price_analysis_table)  # 执行创建price_analysis表的SQL
            self.mysql_conn.commit()  # 提交事务
            logger.info("MySQL表创建成功")
        except Exception as e:
            logger.error(f"MySQL表创建失败: {str(e)}")
            self.mysql_conn.rollback()  # 回滚事务
    
    def extract_ticket_info(self, ticket_text: Optional[Union[str, list, int, float]]) -> Dict[str, Any]:
        """
        从票价文本中提取各类票价信息
        
        Args:
            ticket_text: 门票价格文本，可能是字符串、列表、数字类型
            
        Returns:
            包含提取结果的字典
        """
        if not ticket_text:
            return {
                'ticket': None,  # 门票信息
                'full_price': None,  # 全价票信息
                'half_price': None,  # 半价票信息
                'adult_ticket': None,  # 成人票信息
                'student_child_senior_ticket': None,  # 学生/儿童/老人票信息
                'discount_ticket': None,  # 优惠票信息
                'has_other_fees': False,  # 是否有其他费用
                'has_free_or_discount': False,  # 是否有免票或优惠
                'has_time_periods': False  # 是否分时段
            }
        
        # 处理列表类型的票价数据
        if isinstance(ticket_text, list):
            ticket_text = ' '.join(str(item) for item in ticket_text)  # 将列表转换为字符串
        
        # 处理数字类型的票价
        if isinstance(ticket_text, (int, float)):
            return {
                'ticket': str(ticket_text),  # 将数字转换为字符串
                'full_price': None,
                'half_price': None,
                'adult_ticket': None,
                'student_child_senior_ticket': None,
                'discount_ticket': None,
                'has_other_fees': False,
                'has_free_or_discount': False,
                'has_time_periods': False
            }
            
        # 确保ticket_text是字符串类型
        ticket_text = str(ticket_text)
        
        result = {
            'ticket': None,
            'full_price': None,
            'half_price': None,
            'adult_ticket': None,
            'student_child_senior_ticket': None,
            'discount_ticket': None,
            'has_other_fees': False,
            'has_free_or_discount': False,
            'has_time_periods': False
        }
        
        # 检查是否免费
        if '免费' in ticket_text:
            result['ticket'] = '免费'
        
        # 提取票价
        # 通用票价模式
        price_patterns = [
            r'门票[：:]*(\d+(?:\.\d+)?)',  # 匹配门票价格
            r'票价[：:]*(\d+(?:\.\d+)?)',  # 匹配票价
            r'[\(（]?(\d+(?:\.\d+)?)元[\)）]?',  # 匹配元
            r'价格[：:]*(\d+(?:\.\d+)?)'  # 匹配价格
        ]
        
        for pattern in price_patterns:
            prices = re.findall(pattern, ticket_text)  # 使用正则表达式查找价格
            if prices:
                if not result['ticket']:
                    result['ticket'] = ','.join(prices)  # 将找到的价格用逗号分隔
                break
        
        # 提取全价票
        full_price_patterns = [
            r'全价票[：:]*(\d+(?:\.\d+)?)',  # 匹配全价票
            r'全票[：:]*(\d+(?:\.\d+)?)'  # 匹配全票
        ]
        
        for pattern in full_price_patterns:
            full_prices = re.findall(pattern, ticket_text)  # 查找全价票
            if full_prices:
                result['full_price'] = ','.join(full_prices)  # 将全价票用逗号分隔
                break
        
        # 提取半价票
        half_price_patterns = [
            r'半价票[：:]*(\d+(?:\.\d+)?)',  # 匹配半价票
            r'半票[：:]*(\d+(?:\.\d+)?)'  # 匹配半票
        ]
        
        for pattern in half_price_patterns:
            half_prices = re.findall(pattern, ticket_text)  # 查找半价票
            if half_prices:
                result['half_price'] = ','.join(half_prices)  # 将半价票用逗号分隔
                break
        
        # 提取成人票
        adult_patterns = [
            r'成人票[：:]*(\d+(?:\.\d+)?)',  # 匹配成人票
            r'成人[：:]*(\d+(?:\.\d+)?)'  # 匹配成人
        ]
        
        for pattern in adult_patterns:
            adult_prices = re.findall(pattern, ticket_text)  # 查找成人票
            if adult_prices:
                result['adult_ticket'] = ','.join(adult_prices)  # 将成人票用逗号分隔
                break
        
        # 提取学生/儿童/老人票
        student_child_senior_patterns = [
            r'儿童票[：:]*(\d+(?:\.\d+)?)',  # 匹配儿童票
            r'学生票[：:]*(\d+(?:\.\d+)?)',  # 匹配学生票
            r'老人票[：:]*(\d+(?:\.\d+)?)',  # 匹配老人票
            r'儿童[/／]学生[/／]老人票[：:]*(\d+(?:\.\d+)?)'  # 匹配儿童/学生/老人票
        ]
        
        for pattern in student_child_senior_patterns:
            scs_prices = re.findall(pattern, ticket_text)  # 查找学生/儿童/老人票
            if scs_prices:
                result['student_child_senior_ticket'] = ','.join(scs_prices)  # 将票价用逗号分隔
                break
        
        # 提取优惠票
        discount_patterns = [
            r'优惠票[：:]*(\d+(?:\.\d+)?)',  # 匹配优惠票
            r'优待票[：:]*(\d+(?:\.\d+)?)'  # 匹配优待票
        ]
        
        for pattern in discount_patterns:
            discount_prices = re.findall(pattern, ticket_text)  # 查找优惠票
            if discount_prices:
                result['discount_ticket'] = ','.join(discount_prices)  # 将优惠票用逗号分隔
                break
        
        # 检查是否有其他费用
        other_fees_keywords = [
            '观光车', '游艇', '往返车票', '联票', '展览票', '讲解费'  # 其他费用关键词
        ]
        
        for keyword in other_fees_keywords:
            if keyword in ticket_text:
                result['has_other_fees'] = True  # 如果包含关键词，标记为有其他费用
                break
        
        # 检查是否有免票或优惠
        free_discount_keywords = [
            '免票', '优惠', '优待', '半票优惠'  # 免票或优惠关键词
        ]
        
        for keyword in free_discount_keywords:
            if keyword in ticket_text:
                result['has_free_or_discount'] = True  # 如果包含关键词，标记为有免票或优惠
                break
        
        # 检查是否分时段
        time_period_keywords = [
            '旺季', '淡季', '平日', '周末'  # 分时段关键词
        ]
        
        for keyword in time_period_keywords:
            if keyword in ticket_text:
                result['has_time_periods'] = True  # 如果包含关键词，标记为分时段
                break
        
        return result
    
    def process_data(self):
        """处理MongoDB中的数据并存储到MySQL"""
        try:
            # 从MongoDB查询数据
            attractions = self.mongo_collection.find({}, {
                'name': 1,  # 景区名称
                'city': 1,  # 城市名称
                'ticket': 1,  # 门票信息
                'deep_ticket_price': 1  # 深度票价信息
            })
            
            processed_count = 0  # 已处理的数据计数
            analysis_count = 0  # 需要进一步分析的数据计数
            
            for attraction in attractions:
                try:
                    scenic_name = attraction.get('name', '')  # 获取景区名称
                    city_name = attraction.get('city', '')  # 获取城市名称
                    
                    # 首先检查ticket字段
                    ticket_text = attraction.get('ticket')
                    
                    # 如果ticket为空，则检查deep_ticket_price
                    if ticket_text is None:
                        ticket_text = attraction.get('deep_ticket_price')
                    
                    # 如果两个字段都为空，则跳过
                    if ticket_text is None:
                        continue
                    
                    # 提取票价信息
                    ticket_info = self.extract_ticket_info(ticket_text)
                    
                    # 判断是否需要存入price_analysis表
                    needs_analysis = (
                        ticket_text and 
                        not any([
                            ticket_info['ticket'],
                            ticket_info['full_price'],
                            ticket_info['half_price'],
                            ticket_info['adult_ticket'],
                            ticket_info['student_child_senior_ticket'],
                            ticket_info['discount_ticket']
                        ])
                    )
                    
                    if needs_analysis:
                        # 存入price_analysis表
                        insert_analysis_query = """
                        INSERT INTO price_analysis (scenic_name, city_name, ticket_price)
                        VALUES (%s, %s, %s)
                        """
                        self.mysql_cursor.execute(
                            insert_analysis_query, 
                            (scenic_name, city_name, str(ticket_text))
                        )
                        analysis_count += 1
                    else:
                        # 存入price_process表
                        insert_process_query = """
                        INSERT INTO price_process (
                            scenic_name, city_name, ticket, full_price, half_price,
                            adult_ticket, student_child_senior_ticket, discount_ticket,
                            has_other_fees, has_free_or_discount, has_time_periods
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        self.mysql_cursor.execute(
                            insert_process_query, 
                            (
                                scenic_name, city_name,
                                ticket_info['ticket'],
                                ticket_info['full_price'],
                                ticket_info['half_price'],
                                ticket_info['adult_ticket'],
                                ticket_info['student_child_senior_ticket'],
                                ticket_info['discount_ticket'],
                                ticket_info['has_other_fees'],
                                ticket_info['has_free_or_discount'],
                                ticket_info['has_time_periods']
                            )
                        )
                        processed_count += 1
                    
                    # 每100条提交一次，避免事务过大
                    if (processed_count + analysis_count) % 100 == 0:
                        self.mysql_conn.commit()
                        logger.info(f"已处理 {processed_count + analysis_count} 条数据")
                
                except Exception as e:
                    logger.error(f"处理单条数据时出错: {str(e)}")
                    continue
            
            # 最后提交剩余事务
            self.mysql_conn.commit()
            logger.info(f"数据处理完成，共处理 {processed_count} 条有效数据，{analysis_count} 条需要进一步分析的数据")
            
            return processed_count, analysis_count
        
        except Exception as e:
            logger.error(f"数据处理失败: {str(e)}")
            self.mysql_conn.rollback()
            return 0, 0
    
    def close_connections(self):
        """关闭数据库连接"""
        try:
            if self.mysql_cursor:
                self.mysql_cursor.close()  # 关闭MySQL游标
            if self.mysql_conn:
                self.mysql_conn.close()  # 关闭MySQL连接
            if self.mongo_client:
                self.mongo_client.close()  # 关闭MongoDB客户端
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {str(e)}")

def main():
    """主函数"""
    processor = TicketPriceProcessor(MONGO_CONFIG, MYSQL_CONFIG)
    
    if processor.connect_databases():
        try:
            processed_count, analysis_count = processor.process_data()
            logger.info(f"成功处理 {processed_count} 条数据，{analysis_count} 条数据需要进一步分析")
        except Exception as e:
            logger.error(f"处理过程中发生错误: {str(e)}")
        finally:
            processor.close_connections()
    else:
        logger.error("由于数据库连接失败，无法进行数据处理")

if __name__ == "__main__":
    main()  # 运行主函数
