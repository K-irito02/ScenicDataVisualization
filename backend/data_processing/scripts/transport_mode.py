#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re  # 导入正则表达式模块，用于模式匹配
import pymongo  # 导入pymongo模块，用于连接和操作MongoDB
import mysql.connector  # 导入mysql.connector模块，用于连接和操作MySQL
from mysql.connector import Error  # 导入Error类，用于捕获MySQL连接错误
import collections  # 导入collections模块，用于有序字典

# 交通方式及其别名
TRANSPORT_MODES = {
    "客车": ["客运站", "巴士", "中巴车","中巴", "大巴", "客车站", "班车", "班次", "长途汽车", "长途车站",
           "汽车东站", "汽车西站", "汽车南站", "汽车北站", "客运东站", "客运西站", "客运南站", "客运北站", 
           "汽车总站", "乘坐汽车"],
    "火车": ["火车站"],
    "步行": ["徒步"],
    "三轮车": ["三轮"],
    "动车": ["动车站"],
    "游艇": ["码头", "快艇"],
    "公交": ["公共汽车","各路汽车"],  # 特殊处理
    "地铁": ["轻轨", "交通轨道"],  # 特殊处理
    "观光车": ["区间车","环保车"],
    "专车":["景区交通","景区内交通","直通车","专线车"],
    "自驾": ["驾车", "收费站", "高速", "自驾车","开车", "横穿", "省道", "国道"],
    "包车": ["私家车", "面包车","搭车","租车","打车"],
    "摆渡车": [],
    "船":["坐船","渡船"],
    "高铁":["高铁站"],
    "飞机":["机场"],
    "马":["骑马","骑行"],
    "索道":[],
    "电瓶车":[],
}

# 正则表达式模式
BUS_PATTERN = r'(汽车站(?!长途)|乘坐[0-9A-Z]{1,3}|[0-9]{1,3}路)'
SUBWAY_PATTERN = r'([0-9A-Z]{1,3}号线)'

# 新增的正则表达式模式
SELF_DRIVING_PATTERN = r'([0-9]+(?:省道|国道)|乘车、横穿)(?:\(自驾\))?'
BUS_LINE_PATTERN = r'([0-9A-Z]+、)*[0-9A-Z]+(?:路)?(?:\(公交\))?'
COACH_PATTERN = r'(汽车[东南西北]站|客运[东南西北]站|汽车总站|乘坐.+汽车)(?:\(客车\))?'

class TransportModeProcessor:
    def __init__(self):
        # 初始化MongoDB连接
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")  # 连接到本地MongoDB服务
        self.mongo_db = self.mongo_client["scenic_area"]  # 选择数据库'scenic_area'
        self.mongo_collection = self.mongo_db["china_attractions_copy"]  # 选择集合'china_attractions_copy'
        
        # 初始化MySQL连接
        try:
            self.mysql_connection = mysql.connector.connect(
                host="localhost",  # MySQL服务器地址
                user="root",  # MySQL用户名
                password="3143285505",  # MySQL密码
                charset='utf8mb4'  # 设置字符集为utf8mb4
            )
            self.mysql_cursor = self.mysql_connection.cursor()  # 创建游标对象
            
            # 创建数据库和表
            self._create_database_and_tables()
            
        except Error as e:
            print(f"MySQL连接错误: {e}")  # 打印MySQL连接错误信息
    
    def _create_database_and_tables(self):
        """创建MySQL数据库和表"""
        try:
            # 创建数据库'scenic_area'，如果不存在
            self.mysql_cursor.execute("CREATE DATABASE IF NOT EXISTS scenic_area")
            self.mysql_cursor.execute("USE scenic_area")  # 使用数据库'scenic_area'
            
            # 创建表'transport_mode'，如果不存在
            self.mysql_cursor.execute("""
                CREATE TABLE IF NOT EXISTS transport_mode (
                    id INT AUTO_INCREMENT PRIMARY KEY,  # 自增主键
                    scenic_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,  # 景区名
                    city_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,  # 城市名
                    transport_mode TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,  # 交通方式
                    scheme_count INT,  # 方案数量
                    different_mode_count INT,  # 不同交通方式或组合数量
                    transport_combinations TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci  # 交通方式或组合
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            
            # 创建表'transport_analysed'，如果不存在
            self.mysql_cursor.execute("""
                CREATE TABLE IF NOT EXISTS transport_analysed (
                    id INT AUTO_INCREMENT PRIMARY KEY,  # 自增主键
                    scenic_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,  # 景区名
                    city_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,  # 城市名
                    transport_text TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci  # 原始交通文本
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            
            self.mysql_connection.commit()  # 提交事务
            print("数据库和表创建成功")  # 打印成功信息
            
        except Error as e:
            print(f"创建数据库和表时出错: {e}")  # 打印错误信息
    
    def identify_transport_mode(self, text):
        """识别文本中的交通方式"""
        if not text or text.strip() == "":
            return []  # 如果文本为空，返回空列表
        
        identified_modes = []  # 存储识别到的交通方式
        previous_mode = None  # 存储前一个交通方式
        # 检查每种交通方式及其别名
        for mode, aliases in TRANSPORT_MODES.items():
            if mode in text:
                if mode != previous_mode:
                    identified_modes.append(mode)  # 如果文本中包含交通方式，且与前一次不同，添加到列表
                    previous_mode = mode
                continue
                
            for alias in aliases:
                if alias in text:
                    if mode != previous_mode:
                        identified_modes.append(mode)  # 如果文本中包含别名，且与前一次不同，添加到列表
                        previous_mode = mode
                    break
        
        # 特殊处理公交和地铁
        if re.search(BUS_PATTERN, text):
            identified_modes.append("公交")  # 如果匹配公交模式，添加到列表
        
        if re.search(SUBWAY_PATTERN, text):
            identified_modes.append("地铁")  # 如果匹配地铁模式，添加到列表
            
        # 处理新增的交通方式格式
        if re.search(SELF_DRIVING_PATTERN, text):
            identified_modes.append("自驾")  # 如果匹配自驾模式，添加到列表
            
        if re.search(BUS_LINE_PATTERN, text):
            identified_modes.append("公交")  # 如果匹配公交线路模式，添加到列表
            
        if re.search(COACH_PATTERN, text):
            identified_modes.append("客车")  # 如果匹配客车模式，添加到列表
            
        # 检查括号中的明确标注
        if "(自驾)" in text:
            identified_modes.append("自驾")
        if "(公交)" in text:
            identified_modes.append("公交")
        if "(客车)" in text:
            identified_modes.append("客车")
        
        return list(collections.OrderedDict.fromkeys(identified_modes))  # 保留顺序并去重
    
    def analyze_transport_schemes(self, transport_text):
        """分析交通方案文本，识别方案数量和交通方式组合"""
        if not transport_text or transport_text.strip() == "":
            return None, 0, 0, None  # 如果文本为空，返回默认值
        
        # 将文本按行分割，每行代表一个方案
        lines = [line.strip() for line in transport_text.strip().split('\n') if line.strip()]
        
        scheme_count = 0  # 方案数量
        # 识别每个方案中的交通方式
        scheme_transport_modes = []
        for line in lines:
            modes = self.identify_transport_mode(line)
            if modes:  # 只有当识别到交通方式时才添加
                scheme_count += 1  # 方案数量加1
                scheme_transport_modes.append(modes) # 添加识别到的交通方式
        
        # 如果没有识别到任何交通方式，返回None
        if not scheme_transport_modes:
            return None, 0, 0, None
        
        # 所有识别到的交通方式（去重后）
        all_modes = []
        for modes in scheme_transport_modes:
            for mode in modes:
                if mode not in all_modes:
                    all_modes.append(mode)
        
        # 不同的交通方式组合（去重）
        unique_combinations = []
        for modes in scheme_transport_modes:
            # 将模式列表转换为字符串以方便比较
            mode_str = ','.join(modes)
            if mode_str not in unique_combinations:
                unique_combinations.append(mode_str)
        
        # 交通方式或组合
        transport_combinations = ';'.join(unique_combinations)
        
        # 交通方式（所有去重后的模式）
        transport_mode = ','.join(all_modes) if all_modes else None
        
        return transport_mode, scheme_count, len(unique_combinations), transport_combinations
    
    def process_data(self):
        """处理数据并保存到MySQL"""
        try:
            # 从MongoDB获取数据
            scenic_data = self.mongo_collection.find({})
            
            transport_mode_data = []  # 存储处理后的transport_mode数据
            transport_analysed_data = []  # 存储处理后的transport_analysed数据
            
            for attraction in scenic_data:
                scenic_name = attraction.get('name', '')  # 获取景区名
                city_name = attraction.get('city', '')  # 获取城市名
                transport_text = attraction.get('transport')  # 获取交通文本
                
                if transport_text:
                    # 分析交通方式
                    transport_mode, scheme_count, different_mode_count, transport_combinations = self.analyze_transport_schemes(transport_text)
                    
                    if transport_mode:
                        # 添加到transport_mode表数据
                        transport_mode_data.append((
                            scenic_name,
                            city_name,
                            transport_mode,
                            scheme_count,
                            different_mode_count,
                            transport_combinations
                        ))
                    else:
                        # 如果没有识别到交通方式，添加到transport_analysed表
                        transport_analysed_data.append((
                            scenic_name,
                            city_name,
                            transport_text
                        ))
            
            # 批量插入transport_mode表
            if transport_mode_data:
                self.mysql_cursor.executemany("""
                    INSERT INTO transport_mode 
                    (scenic_name, city_name, transport_mode, scheme_count, different_mode_count, transport_combinations)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, transport_mode_data)
            
            # 批量插入transport_analysed表
            if transport_analysed_data:
                self.mysql_cursor.executemany("""
                    INSERT INTO transport_analysed
                    (scenic_name, city_name, transport_text)
                    VALUES (%s, %s, %s)
                """, transport_analysed_data)
            
            self.mysql_connection.commit()  # 提交事务
            print(f"数据处理完成，添加了{len(transport_mode_data)}条transport_mode记录和{len(transport_analysed_data)}条transport_analysed记录")
            
        except Exception as e:
            print(f"处理数据时出错: {e}")  # 打印错误信息
    
    def close_connections(self):
        """关闭数据库连接"""
        if hasattr(self, 'mysql_cursor') and self.mysql_cursor:
            self.mysql_cursor.close()  # 关闭MySQL游标
        if hasattr(self, 'mysql_connection') and self.mysql_connection:
            self.mysql_connection.close()  # 关闭MySQL连接
        if hasattr(self, 'mongo_client') and self.mongo_client:
            self.mongo_client.close()  # 关闭MongoDB连接
        print("数据库连接已关闭")  # 打印关闭连接信息

if __name__ == "__main__":
    processor = TransportModeProcessor()  # 创建TransportModeProcessor实例
    try:
        processor.process_data()  # 处理数据
    finally:
        processor.close_connections()  # 关闭数据库连接
