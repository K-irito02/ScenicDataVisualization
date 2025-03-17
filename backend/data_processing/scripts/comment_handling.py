#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
景区评论数据处理及分析模块
用于处理MongoDB中的景区评论数据，进行预处理、情感分析、文本挖掘等操作，
并将结果存入MySQL数据库
"""

import re
import os
import jieba
import jieba.posseg as pseg
import pymongo
import pymysql
import numpy as np
from collections import Counter
from hanziconv import HanziConv
from pypinyin import lazy_pinyin, Style


class CommentHandler:
    """景区评论数据处理类"""
    
    def __init__(self, mongo_config=None, mysql_config=None):
        """
        初始化函数
        
        Args:
            mongo_config: MongoDB配置信息，包括host, port, db_name等
            mysql_config: MySQL配置信息，包括host, port, user, password, db_name等
        """
        # 默认MongoDB配置
        self.mongo_config = mongo_config or {
            'host': 'localhost',
            'port': 27017,
            'db_name': 'scenic_area',
            'collection_name': 'china_attractions_copy'
        }
        
        # 默认MySQL配置
        self.mysql_config = mysql_config or {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '3143285505',
            'db_name': 'scenic_area',
            'table_name': 'comment_handling'
        }
        
        # 加载情感词典
        self.sentiment_dict, self.degree_dict = self._load_sentiment_dict()
        
        # 加载停用词列表
        self.stopwords = self._load_stopwords()
        
        # 加载否定词列表
        self.negation_words = self._load_negation_words()
        
        # 领域停用词（景区相关的常见词汇）
        self.domain_stopwords = [
            '景区', '景点', '门票', '旅游', '观光', '游玩', '游客', 
            '自驾', '出行', '导游', '旅行', '行程', '出游', '景色',
            '风景', '风光', '景观', '游览', '参观', '路线', '酒店',
            '到达', '离开', '路途', '路程', '车程', '住宿', '特产',
            '特色', '天气', '时间', '时候', '还是', '就是', '确实', 
            '感觉', '真的', '比较', '应该', '已经', '所以', '因为', 
            '只是', '但是', '有点', '不过', '如果', '然后', '基本', 
            '完全', '一定'
        ]
        
        # 将领域停用词添加到停用词列表
        self.stopwords.extend(self.domain_stopwords)
        
        # 连接MongoDB
        self.mongo_client = pymongo.MongoClient(
            host=self.mongo_config['host'],
            port=self.mongo_config['port']
        )
        self.mongo_db = self.mongo_client[self.mongo_config['db_name']]
        self.mongo_collection = self.mongo_db[self.mongo_config['collection_name']]
        
        # 连接MySQL
        self.mysql_conn = pymysql.connect(
            host=self.mysql_config['host'],
            port=self.mysql_config['port'],
            user=self.mysql_config['user'],
            password=self.mysql_config['password'],
            db=self.mysql_config['db_name'],
            charset='utf8mb4'
        )
        self.mysql_cursor = self.mysql_conn.cursor()
        
        # 创建MySQL表
        self._create_mysql_table()

    def _load_sentiment_dict(self):
        """
        加载BosonNLP情感词典
        
        Returns:
            tuple: (情感词典, 程度词典)
            情感词典格式为 {词: 情感值}
            程度词典格式为 {词: 程度值}
        """
        sentiment_dict = {}
        degree_dict = {}
        
        # BosonNLP情感词典文件路径
        dict_files = {
            'pos': "正面情绪词.txt",  # 积极词典
            'neg': "负面情绪词.txt",  # 消极词典
            'pos_ext': "扩展积极词典.txt",  # 扩展积极词典
            'neg_ext': "扩展消极词典.txt",  # 扩展消极词典
            'degree': "程度副词.txt",  # 程度词典
        }
        
        # 基础目录路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            # 加载积极词典
            with open(os.path.join(base_dir, dict_files['pos']), 'r', encoding='utf-8') as f:
                for word in f:
                    word = word.strip()
                    if word:
                        sentiment_dict[word] = 1.0
                        
            # 加载消极词典
            with open(os.path.join(base_dir, dict_files['neg']), 'r', encoding='utf-8') as f:
                for word in f:
                    word = word.strip()
                    if word:
                        sentiment_dict[word] = -1.0
                        
            # 加载扩展积极词典
            with open(os.path.join(base_dir, dict_files['pos_ext']), 'r', encoding='utf-8') as f:
                for line in f:
                    word, score = line.strip().split()
                    sentiment_dict[word] = float(score)
                    
            # 加载扩展消极词典
            with open(os.path.join(base_dir, dict_files['neg_ext']), 'r', encoding='utf-8') as f:
                for line in f:
                    word, score = line.strip().split()
                    sentiment_dict[word] = -float(score)
                    
            # 加载程度词典
            with open(os.path.join(base_dir, dict_files['degree']), 'r', encoding='utf-8') as f:
                for line in f:
                    word, degree = line.strip().split()
                    degree_dict[word] = float(degree)
                    
        except FileNotFoundError as e:
            print(f"警告：找不到情感词典文件: {e}")
        
        return sentiment_dict, degree_dict

    def _load_stopwords(self):
        """
        加载停用词表
        
        Returns:
            list: 停用词列表
        """
        # 基础停用词列表
        with open(os.path.join(os.path.dirname(__file__), '停用词.txt'), 'r', encoding='utf-8') as f:
            basic_stopwords = f.read().splitlines()
        
        return basic_stopwords

    def _load_negation_words(self):
        """
        加载否定词表
        
        Returns:
            list: 否定词列表
        """
        # 基础否定词列表
        with open(os.path.join(os.path.dirname(__file__), '否定词.txt'), 'r', encoding='utf-8') as f:
            negation_words = f.read().splitlines()
        
        return negation_words

    def _create_mysql_table(self):
        """创建MySQL数据表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS {} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL COMMENT '景区名',
            city VARCHAR(100) COMMENT '城市',
            comment_count INT COMMENT '评论条数',
            emo_tend VARCHAR(10) COMMENT '情感倾向（良、中、优）',
            emo_score FLOAT COMMENT '情感得分',
            emo_inten FLOAT COMMENT '情感强度',
            keywords TEXT COMMENT '关键词及其频次（格式：词:频次，用英文逗号隔开）',
            highFre_words TEXT COMMENT '高频词及其频次（格式：词:频次，用英文逗号隔开）',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='景区评论处理结果表';
        """.format(self.mysql_config['table_name'])
        
        self.mysql_cursor.execute(create_table_sql)
        self.mysql_conn.commit()

    def preprocess_text(self, text):
        """
        文本预处理
        
        Args:
            text: 原始文本
            
        Returns:
            str: 预处理后的文本
        """
        if not text or not isinstance(text, str):
            return ""
            
        # 1. 去除URL
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # 2. 去除HTML标签
        text = re.sub(r'<.*?>', '', text)
        
        # 3. 去除特殊字符和标点符号，但保留中文标点
        text = re.sub(r'[^\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef\s]', '', text)
        
        # 4. 替换多个空格为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        # 5. 数字统一处理（这里简单替换为"数字"）
        text = re.sub(r'\d+(\.\d+)?', '数字', text)
        
        # 6. 繁体转简体
        text = HanziConv.toSimplified(text)
        
        # 7. 处理换行符
        text = re.sub(r'[\n\r]+', ' ', text)
        
        # 8. 去除首尾空格
        text = text.strip()
        
        return text

    def normalize_text(self, text):
        """
        文本标准化
        
        Args:
            text: 预处理后的文本
            
        Returns:
            str: 标准化后的文本
        """
        if not text:
            return ""
        
        # 1. 大小写统一（如果有英文的话）
        text = text.lower()
            
        return text

    def segment_text(self, text):
        """
        中文分词
        
        Args:
            text: 标准化后的文本
            
        Returns:
            list: 分词结果列表
        """
        if not text:
            return []
            
        # 使用jieba进行分词
        words = jieba.lcut(text)
        
        return words

    def filter_by_pos(self, text, allowed_pos=None):
        """
        按词性过滤
        
        Args:
            text: 标准化后的文本
            allowed_pos: 允许的词性列表
            
        Returns:
            list: 过滤停用词后的词列表
        """
        if not text:
            return []
            
        # 使用jieba进行词性标注
        words_pos = pseg.cut(text)
        
        # 过滤停用词
        filtered_words = []
        for word, flag in words_pos:
            if word not in self.stopwords and len(word) > 1:
                if allowed_pos is None or flag in allowed_pos:
                    filtered_words.append((word, flag))
        
        return filtered_words

    def filter_keywords(self, words_with_pos):
        """
        过滤关键词（仅保留特定词性）
        
        Args:
            words_with_pos: 带词性标注的词列表
            
        Returns:
            list: 过滤后的关键词列表
        """
        # 关键词允许的词性
        allowed_pos = {'n', 'nr', 'nt', 'nz', 'nl', 'ng', 'm', 'x'}
        
        return [word for word, flag in words_with_pos if flag in allowed_pos]

    def filter_high_frequency_words(self, words_with_pos):
        """
        过滤高频词（仅保留特定词性）
        
        Args:
            words_with_pos: 带词性标注的词列表
            
        Returns:
            list: 过滤后的高频词列表
        """
        # 高频词允许的词性
        allowed_pos = {'n', 'nr', 'nt', 'nz', 'nl', 'ng', 'v', 'vn', 'vi', 'vl', 'a', 'an', 'ag', 'al', 'm', 'e', 'o', 'wt'}
        
        return [word for word, flag in words_with_pos if flag in allowed_pos]

    def analyze_sentiment(self, words):
        """
        情感分析
        
        Args:
            words: 过滤后的词列表
            
        Returns:
            tuple: (情感倾向, 情感得分, 情感强度)
        """
        if not words:
            return "中", 0, 0
            
        # 初始化情感得分
        sentiment_score = 0
        
        # 情感强度
        intensity = 0
        
        # 否定词的影响范围（默认为2个词）
        negation_scope = 2
        
        # 当前否定词的影响范围计数
        negation_count = 0
        
        # 是否在否定词影响范围内
        is_negated = False
        
        # 当前程度词的程度值
        current_degree = 1.0
        
        # 计算情感得分
        for word, flag in words:
            # 检查是否为否定词
            if word in self.negation_words:
                is_negated = True
                negation_count = 0
                continue
                
            # 检查是否为程度词
            if word in self.degree_dict:
                current_degree = self.degree_dict[word]
                continue
                
            # 如果当前词在情感词典中
            if word in self.sentiment_dict:
                score = self.sentiment_dict[word]
                
                # 应用程度词的影响
                score *= current_degree
                
                # 如果在否定词影响范围内，则反转情感极性
                if is_negated and negation_count < negation_scope:
                    score = -score
                
                sentiment_score += score
                intensity += abs(score)
                
                # 重置程度值
                current_degree = 1.0
            
            # 更新否定词影响范围计数
            if is_negated:
                negation_count += 1
                if negation_count >= negation_scope:
                    is_negated = False
        
        # 平均情感强度
        if len(words) > 0:
            intensity = intensity / len(words)
        
        # 确定情感倾向（根据BosonNLP的标准调整阈值）
        if sentiment_score / len(words) > 0.09:  # 提高积极阈值
            sentiment = "优"
        elif sentiment_score / len(words) < 0.03:  # 调整消极阈值
            sentiment = "良"
        else:
            sentiment = "中"

        return sentiment, round(sentiment_score, 2), round(intensity, 2)

    def extract_keywords(self, words_with_pos, top_n=10, for_keywords=True):
        """
        关键词提取
        
        Args:
            words_with_pos: 带词性标注的词列表
            top_n: 提取的关键词数量
            for_keywords: 是否是提取关键词（True）还是高频词（False）
            
        Returns:
            list: 关键词及其频次列表
        """
        if not words_with_pos or len(words_with_pos) == 0:
            return []
            
        # 根据不同用途过滤词性
        if for_keywords:
            filtered_words = self.filter_keywords(words_with_pos)
        else:
            filtered_words = self.filter_high_frequency_words(words_with_pos)
            
        if not filtered_words:
            return []
            
        # 统计词频
        word_counter = Counter(filtered_words)
        
        # 获取出现频率最高的词
        top_words = word_counter.most_common(top_n)
        
        # 提取关键词及其频次
        keywords = [f"{word}:{count}" for word, count in top_words]
        
        return keywords

    def process_comments(self, attraction):
        """
        处理单个景点的评论
        
        Args:
            attraction: MongoDB中的景点文档
            
        Returns:
            dict: 处理结果
        """
        name = attraction.get('name', '')
        city = attraction.get('city', '')
        comments = attraction.get('comments', [])
        comment_count = attraction.get('comment_count', len(comments))
        
        # 所有评论合并为一个字符串进行处理
        all_comments_text = ' '.join(comments)
        
        # 文本预处理
        preprocessed_text = self.preprocess_text(all_comments_text)
        
        # 文本标准化
        normalized_text = self.normalize_text(preprocessed_text)
        
        # 过滤停用词
        filtered_words = self.filter_by_pos(normalized_text)
        
        # 情感分析
        emo_tend, emo_score, emo_inten = self.analyze_sentiment(filtered_words)
        
        # 提取关键词（最多10个）
        keywords = self.extract_keywords(filtered_words, 10, for_keywords=True)
        
        # 提取高频词（最多20个）
        highFre_words = self.extract_keywords(filtered_words, 20, for_keywords=False)
        
        # 构建结果
        result = {
            'name': name,
            'city': city,
            'comment_count': comment_count,
            'emo_tend': emo_tend,
            'emo_score': emo_score,
            'emo_inten': emo_inten,
            'keywords': ','.join(keywords),
            'highFre_words': ','.join(highFre_words)
        }
        
        return result

    def save_to_mysql(self, data):
        """
        保存处理结果到MySQL
        
        Args:
            data: 处理结果数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 构建INSERT SQL语句
            insert_sql = """
            INSERT INTO {} (name, city, comment_count, emo_tend, emo_score, emo_inten, keywords, highFre_words)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """.format(self.mysql_config['table_name'])
            
            # 执行SQL
            self.mysql_cursor.execute(
                insert_sql,
                (
                    data['name'],
                    data['city'],
                    data['comment_count'],
                    data['emo_tend'],
                    data['emo_score'],
                    data['emo_inten'],
                    data['keywords'],
                    data['highFre_words']
                )
            )
            
            # 提交事务
            self.mysql_conn.commit()
            
            return True
        except Exception as e:
            print(f"保存数据到MySQL失败: {e}")
            self.mysql_conn.rollback()
            return False

    def process_all_attractions(self):
        """
        处理所有景点数据
        
        Returns:
            int: 处理成功的数量
        """
        # 获取所有景点数据
        attractions = self.mongo_collection.find()
        
        # 计数器
        success_count = 0
        
        # 处理每个景点
        for attraction in attractions:
            if 'comments' in attraction and attraction['comments']:
                # 处理评论
                result = self.process_comments(attraction)
                
                # 保存到MySQL
                if self.save_to_mysql(result):
                    success_count += 1
                    print(f"成功处理景点: {result['name']}")
        
        return success_count

    def close(self):
        """关闭数据库连接"""
        if self.mongo_client:
            self.mongo_client.close()
            
        if self.mysql_conn:
            self.mysql_cursor.close()
            self.mysql_conn.close()


def main():
    """主函数"""
    # 实例化评论处理类
    handler = CommentHandler()
    
    try:
        # 处理所有景点
        success_count = handler.process_all_attractions()
        print(f"共成功处理 {success_count} 个景点")
    finally:
        # 关闭连接
        handler.close()


if __name__ == "__main__":
    main()
