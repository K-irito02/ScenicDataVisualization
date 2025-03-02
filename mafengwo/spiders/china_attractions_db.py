#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
马蜂窝全国景点爬虫（数据库存储URL版本）
使用Redis存储URL队列和爬取结果
支持分布式爬取
"""

import json
import time
import random
import redis
import threading
import os
from datetime import datetime
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from mafengwo.items_distributed import MafengwoDistributedItem

class ChinaAttractionsDBSpider(scrapy.Spider):
    """
    马蜂窝全国景点爬虫
    使用数据库存储URL而不是yield传递请求
    """
    name = "china_attractions_db"
    allowed_domains = ["mafengwo.cn"]
    start_urls = ["https://www.mafengwo.cn/mdd/"]  # 马蜂窝目的地页面
    
    # 设置更长的下载超时和重试次数
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 60,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 202],
        'DOWNLOAD_DELAY': 5,  # 增加下载延迟
        'CONCURRENT_REQUESTS': 1,  # 降低并发请求数
        'COOKIES_ENABLED': True,
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
        'HTTPERROR_ALLOWED_CODES': [202],  # 允许处理202状态码
    }
    
    # 随机User-Agent列表
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    ]

    def __init__(self, node_id='node1', is_master=False, task_type='all', redis_host='localhost', checkpoint_interval=300, *args, **kwargs):
        super(ChinaAttractionsDBSpider, self).__init__(*args, **kwargs)
        self.node_id = node_id
        
        # 确保is_master参数正确转换为布尔值
        if isinstance(is_master, str):
            self.is_master = is_master.lower() == 'true'
        else:
            self.is_master = bool(is_master)
        
        self.logger.info(f"爬虫初始化: 节点ID={self.node_id}, 是否主节点={self.is_master}")
        
        self.task_type = task_type  # 'all', 'cities', 'list', 'detail'
        self.checkpoint_interval = int(checkpoint_interval)  # 检查点保存间隔（秒）
        
        # 初始化 Selenium 相关配置
        self.options = webdriver.EdgeOptions()
        
        # 添加浏览器参数
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument(f'user-agent={random.choice(self.USER_AGENTS)}')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--enable-unsafe-swiftshader')
        self.options.add_argument('--disable-software-rasterizer')
        
        # 创建Service对象
        self.service = Service(executable_path="E:\\edgedriver\\msedgedriver.exe")
        
        # 创建结果目录
        os.makedirs('results', exist_ok=True)
        
        # 创建断点续爬状态目录
        self.checkpoint_dir = f'crawls/{self.name}_{self.node_id}/checkpoints'
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # 初始化Redis连接
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=6379,
                db=0,
                password='3143285505',
                decode_responses=False
            )
            self.logger.info(f"Redis连接成功初始化，连接到 {redis_host}")
            
            # 只有主节点才初始化队列
            if self.is_master:
                self.logger.info("作为主节点初始化队列")
                # 检查是否有断点续爬状态
                if self.load_checkpoint():
                    self.logger.info("已从断点恢复爬虫状态")
                else:
                    # 清空其他队列，但保留cities_urls队列
                    self.redis_client.delete(f"{self.name}:list_urls")
                    self.redis_client.delete(f"{self.name}:detail_urls")
                    
                    # 检查cities_urls队列是否为空，如果为空则添加起始URL
                    if self.redis_client.llen(f"{self.name}:cities_urls") == 0:
                        # 将起始URL添加到城市队列
                        self.redis_client.lpush(f"{self.name}:cities_urls", self.start_urls[0])
                        self.logger.info(f"主节点已初始化URL队列，添加起始URL: {self.start_urls[0]}")
            
            # 记录爬虫启动时间和状态
            self.start_time = datetime.now()
            self.save_spider_status("started")
            
            # 启动定期保存检查点的线程
            self.stop_checkpoint_thread = False
            self.checkpoint_thread = threading.Thread(target=self.periodic_checkpoint_saver)
            self.checkpoint_thread.daemon = True
            self.checkpoint_thread.start()
            self.logger.info(f"已启动定期保存检查点线程，间隔: {self.checkpoint_interval}秒")
            
        except Exception as e:
            self.logger.error(f"Redis连接初始化失败: {str(e)}")
            self.redis_client = None
    
    def periodic_checkpoint_saver(self):
        """定期保存检查点的线程函数"""
        while not self.stop_checkpoint_thread:
            # 等待指定的间隔时间
            for _ in range(self.checkpoint_interval):
                if self.stop_checkpoint_thread:
                    break
                time.sleep(1)
            
            if not self.stop_checkpoint_thread:
                self.logger.info("定期保存检查点...")
                self.save_checkpoint()
    
    def save_spider_status(self, status):
        """保存爬虫状态"""
        try:
            status_data = {
                "status": status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "node_id": self.node_id,
                "task_type": self.task_type
            }
            
            # 保存到Redis
            self.redis_client.set(
                f"{self.name}:status:{self.node_id}", 
                json.dumps(status_data, ensure_ascii=False)
            )
            
            # 保存到本地文件
            status_file = os.path.join(self.checkpoint_dir, f"status_{self.node_id}.json")
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=4)
                
            self.logger.info(f"已保存爬虫状态: {status}")
        except Exception as e:
            self.logger.error(f"保存爬虫状态失败: {str(e)}")
    
    def save_checkpoint(self):
        """保存断点续爬检查点"""
        try:
            # 获取当前队列状态
            cities_urls_count = self.redis_client.llen(f"{self.name}:cities_urls")
            list_urls_count = self.redis_client.llen(f"{self.name}:list_urls")
            detail_urls_count = self.redis_client.llen(f"{self.name}:detail_urls")
            
            # 获取已处理的URL数量
            cities_processed = self.redis_client.scard(f"{self.name}:cities:dupefilter")
            list_processed = self.redis_client.scard(f"{self.name}:list:dupefilter")
            detail_processed = self.redis_client.scard(f"{self.name}:detail:dupefilter")
            
            # 获取已保存的数据数量
            city_count = len(self.redis_client.keys("china:city:info:*"))
            attraction_count = self.redis_client.scard("china:attractions:all")
            
            checkpoint_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "node_id": self.node_id,
                "task_type": self.task_type,
                "queue_status": {
                    "cities_urls": cities_urls_count,
                    "list_urls": list_urls_count,
                    "detail_urls": detail_urls_count
                },
                "processed_status": {
                    "cities": cities_processed,
                    "list": list_processed,
                    "detail": detail_processed
                },
                "data_status": {
                    "cities": city_count,
                    "attractions": attraction_count
                }
            }
            
            # 保存检查点到文件
            checkpoint_file = os.path.join(self.checkpoint_dir, f"checkpoint_{self.node_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=4)
            
            # 更新最新检查点文件
            latest_checkpoint_file = os.path.join(self.checkpoint_dir, f"checkpoint_{self.node_id}_latest.json")
            with open(latest_checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=4)
                
            self.logger.info(f"已保存断点续爬检查点: {checkpoint_file}")
            return True
        except Exception as e:
            self.logger.error(f"保存断点续爬检查点失败: {str(e)}")
            return False
    
    def load_checkpoint(self):
        """加载断点续爬检查点"""
        try:
            # 检查是否存在最新检查点文件
            latest_checkpoint_file = os.path.join(self.checkpoint_dir, f"checkpoint_{self.node_id}_latest.json")
            if not os.path.exists(latest_checkpoint_file):
                self.logger.info("未找到断点续爬检查点文件，将从头开始爬取")
                return False
            
            # 加载检查点数据
            with open(latest_checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            self.logger.info(f"已加载断点续爬检查点: {checkpoint_data['timestamp']}")
            
            # 检查队列是否为空，如果为空且有已处理的数据，则重新初始化队列
            cities_urls_count = self.redis_client.llen(f"{self.name}:cities_urls")
            list_urls_count = self.redis_client.llen(f"{self.name}:list_urls")
            detail_urls_count = self.redis_client.llen(f"{self.name}:detail_urls")
            
            if cities_urls_count == 0 and list_urls_count == 0 and detail_urls_count == 0:
                # 检查是否有未完成的任务
                if self.task_type == 'all' or self.task_type == 'cities':
                    if checkpoint_data['processed_status']['cities'] < 10:  # 假设至少应该有10个城市
                        self.redis_client.lpush(f"{self.name}:cities_urls", "https://www.mafengwo.cn/mdd/")
                        self.logger.info("已重新初始化城市列表页URL队列")
                
                self.logger.info("已从断点恢复爬虫状态")
            
            return True
        except Exception as e:
            self.logger.error(f"加载断点续爬检查点失败: {str(e)}")
            return False

    def start_requests(self):
        """根据任务类型处理不同的URL队列"""
        # 检查城市URL队列是否为空，如果为空且是主节点，则添加起始URL
        cities_urls_count = self.redis_client.llen(f"{self.name}:cities_urls")
        if cities_urls_count == 0 and self.is_master:
            self.logger.info(f"城市URL队列为空，添加起始URL: {self.start_urls[0]}")
            self.redis_client.lpush(f"{self.name}:cities_urls", self.start_urls[0])
            # 重新获取队列长度
            cities_urls_count = self.redis_client.llen(f"{self.name}:cities_urls")
            self.logger.info(f"城市URL队列现在有 {cities_urls_count} 个URL")
        
        # 打印当前队列状态
        self.logger.info(f"当前队列状态:")
        self.logger.info(f"城市列表页URL队列: {self.redis_client.llen(f'{self.name}:cities_urls')}")
        self.logger.info(f"景点列表页URL队列: {self.redis_client.llen(f'{self.name}:list_urls')}")
        self.logger.info(f"详情页URL队列: {self.redis_client.llen(f'{self.name}:detail_urls')}")
        
        # 根据任务类型处理不同的URL队列
        if self.task_type == 'all' or self.task_type == 'cities':
            # 检查cities_urls队列中是否有URL
            if cities_urls_count > 0:
                self.logger.info(f"发现 {cities_urls_count} 个城市列表页URL，开始处理")
                self.process_cities_urls()
            else:
                self.logger.info("城市列表页URL队列为空，跳过处理")
        
        if self.task_type == 'all' or self.task_type == 'list':
            # 检查list_urls队列中是否有URL
            list_urls_count = self.redis_client.llen(f"{self.name}:list_urls")
            if list_urls_count > 0:
                self.logger.info(f"发现 {list_urls_count} 个景点列表页URL，开始处理")
                self.process_list_urls()
            else:
                self.logger.info("景点列表页URL队列为空，跳过处理")
        
        if self.task_type == 'all' or self.task_type == 'detail':
            # 检查detail_urls队列中是否有URL
            detail_urls_count = self.redis_client.llen(f"{self.name}:detail_urls")
            if detail_urls_count > 0:
                self.logger.info(f"发现 {detail_urls_count} 个景点详情页URL，开始处理")
                self.process_detail_urls()
            else:
                self.logger.info("景点详情页URL队列为空，跳过处理")
        
        # 返回空列表，因为我们使用数据库存储URL而不是yield传递请求
        return []

    def process_cities_urls(self):
        """处理城市列表页URL队列"""
        # 从Redis队列中获取一个城市列表页URL
        url_data = self.redis_client.rpop(f"{self.name}:cities_urls")
        if url_data:
            try:
                url = url_data.decode('utf-8')
                # 检查URL是否已经被处理过
                if not self.redis_client.sismember(f"{self.name}:cities:dupefilter", url):
                    self.logger.info(f"处理城市列表页: {url}")
                    # 将URL标记为已处理
                    self.redis_client.sadd(f"{self.name}:cities:dupefilter", url)
                    # 解析城市列表页
                    self.parse_cities_list(url)
                else:
                    self.logger.info(f"城市列表页已处理过: {url}")
            except Exception as e:
                self.logger.error(f"处理城市列表页URL时出错: {str(e)}")
                # 如果处理出错，将URL放回队列
                self.redis_client.lpush(f"{self.name}:cities_urls", url_data)
        else:
            self.logger.info("城市列表页URL队列为空")
            
        # 如果任务类型包含列表页，则处理列表页URL队列
        if self.task_type == 'all' or self.task_type == 'list':
            self.process_list_urls()

    def parse_cities_list(self, url):
        """使用selenium爬取马蜂窝城市列表页面，并使用Scrapy选择器解析"""
        self.logger.info("开始爬取城市列表")
        try:
            # 初始化 Selenium WebDriver
            driver = webdriver.Edge(service=self.service, options=self.options)
            
            # 访问城市列表页面
            driver.get(url)
            
            # 增加初始等待时间
            time.sleep(random.uniform(5, 8))
            
            # 执行JavaScript来模拟真实浏览器
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            wait = WebDriverWait(driver, 30)
            
            # 等待页面加载完成
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'hot-list')]")))
            except TimeoutException:
                self.logger.warning("等待页面加载超时，尝试继续处理")
            
            # 保存页面源码以便调试
            with open(f'results/cities_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            
            # 获取页面源码并创建Scrapy选择器
            html_content = driver.page_source
            response = scrapy.Selector(text=html_content)
            
            # 使用Scrapy选择器解析页面
            base_xpath = '/html/body/div[2]/div[2]/div/div[3]/div[1]'
            
            # 处理直辖市
            try:
                # 获取直辖市区域
                municipalities_dl = response.xpath(f'{base_xpath}/div[1]/dl[1]')
                if municipalities_dl:
                    # 获取"直辖市"标题
                    title = municipalities_dl.xpath('./dt/text()').get()
                    if not title:
                        title = "直辖市"
                    
                    # 获取直辖市的链接和名称
                    municipality_links = municipalities_dl.xpath('./dd/a/@href').getall()
                    municipality_names = municipalities_dl.xpath('./dd/a/text()').getall()
                    
                    # 将直辖市信息添加到结果中
                    for name, link in zip(municipality_names, municipality_links):
                        try:
                            name = name.strip()
                            # 修改链接格式
                            if link and 'travel-scenic-spot/mafengwo' in link:
                                # 提取ID
                                city_id = link.split('/')[-1].replace('.html', '')
                                # 构建新的链接（景点列表页面）
                                attractions_list_url = f"https://www.mafengwo.cn/jd/{city_id}/gonglve.html"
                                
                                # 构建完整链接
                                full_link = urljoin("https://www.mafengwo.cn", link)
                                
                                city_info = {
                                    "type": title,
                                    "name": name,
                                    "link": full_link,
                                    "city_id": city_id,
                                    "attractions_list_url": attractions_list_url
                                }
                                
                                # 将景点列表页URL添加到Redis队列
                                self.redis_client.lpush(f"{self.name}:list_urls", attractions_list_url)
                                self.logger.info(f"已将城市 {name} 的景点列表页URL添加到队列: {attractions_list_url}")
                                
                                # 同时将城市基本信息存储到Redis
                                info_key = f"china:city:info:{city_id}"
                                self.redis_client.set(info_key, json.dumps(city_info, ensure_ascii=False))
                        except Exception as e:
                            self.logger.error(f"处理直辖市信息时出错: {str(e)}")
            except Exception as e:
                self.logger.error(f"处理直辖市区域时出错: {str(e)}")
            
            # 处理其他省份
            try:
                # 统计省份总数
                total_provinces = 0
                provinces = []
                
                # 遍历两个div区域
                for div_index in [1, 2]:
                    # 获取所有省份的dl元素（第一个div跳过直辖市的dl，第二个div不跳过）
                    if div_index == 1:
                        province_dls = response.xpath(f'{base_xpath}/div[{div_index}]/dl[position()>1]')

                    if div_index == 2:
                        province_dls = response.xpath(f'{base_xpath}/div[{div_index}]/dl')
                        
                    self.logger.info(f"在div[{div_index}]中找到 {len(province_dls)} 个省份dl元素")
                    
                    for dl in province_dls:
                        # 获取dt中的所有省份链接和名称
                        province_links = dl.xpath('./dt/a/@href').getall()
                        province_names = dl.xpath('./dt/a/text()').getall()
                        
                        # 将省份信息添加到结果中
                        for name, link in zip(province_names, province_links):
                            try:
                                name = name.strip()
                                # 修改链接格式
                                if link and 'travel-scenic-spot/mafengwo' in link:
                                    # 提取ID
                                    city_id = link.split('/')[-1].replace('.html', '')
                                    # 构建新的链接（景点列表页面）
                                    attractions_list_url = f"https://www.mafengwo.cn/jd/{city_id}/gonglve.html"
                                    
                                    # 构建完整链接
                                    full_link = urljoin("https://www.mafengwo.cn", link)
                                    
                                    city_info = {
                                        "type": "省份",
                                        "name": name,
                                        "link": full_link,
                                        "city_id": city_id,
                                        "attractions_list_url": attractions_list_url
                                    }
                                    
                                    # 将景点列表页URL添加到Redis队列
                                    self.redis_client.lpush(f"{self.name}:list_urls", attractions_list_url)
                                    self.logger.info(f"已将省份 {name} 的景点列表页URL添加到队列: {attractions_list_url}")
                                    
                                    # 同时将城市基本信息存储到Redis
                                    info_key = f"china:city:info:{city_id}"
                                    self.redis_client.set(info_key, json.dumps(city_info, ensure_ascii=False))
                                    
                                    # 添加到省份列表
                                    provinces.append(city_info)
                                    total_provinces += 1
                            except Exception as e:
                                self.logger.error(f"处理省份信息时出错: {str(e)}")
                
                # 输出统计信息
                self.logger.info(f"总共解析了 {total_provinces} 个省份")
            except Exception as e:
                self.logger.error(f"处理省份区域时出错: {str(e)}")
            
            # 关闭driver
            driver.quit()
            
        except Exception as e:
            self.logger.error(f"爬取城市列表时出错: {str(e)}")
            if 'driver' in locals():
                driver.quit()

    def process_list_urls(self):
        """处理景点列表页URL队列"""
        # 从Redis队列中获取一个景点列表页URL
        url_data = self.redis_client.rpop(f"{self.name}:list_urls")
        if url_data:
            try:
                # 尝试解析为JSON，如果失败则直接使用字符串
                try:
                    url_info = json.loads(url_data.decode('utf-8'))
                    url = url_info.get('url')
                    city_info = url_info.get('city_info')
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # 如果不是JSON格式，则直接使用字符串
                    url = url_data.decode('utf-8')
                    city_info = None
                    
                # 确保URL不为空
                if not url:
                    url = url_data.decode('utf-8')
                
                # 检查URL是否已经被处理过
                if not self.redis_client.sismember(f"{self.name}:list:dupefilter", url):
                    self.logger.info(f"处理景点列表页: {url}")
                    # 将URL标记为已处理
                    self.redis_client.sadd(f"{self.name}:list:dupefilter", url)
                    # 解析景点列表页
                    self.parse_attractions_list(url, city_info)
                else:
                    self.logger.info(f"景点列表页已处理过: {url}")
            except Exception as e:
                self.logger.error(f"处理景点列表页URL时出错: {str(e)}")
                # 如果处理出错，将URL放回队列
                self.redis_client.lpush(f"{self.name}:list_urls", url_data)
        else:
            self.logger.info("景点列表页URL队列为空")
            
        # 如果任务类型包含详情页，则处理详情页URL队列
        if self.task_type == 'all' or self.task_type == 'detail':
            self.process_detail_urls()

    def parse_attractions_list(self, url, city_info=None):
        """使用selenium爬取马蜂窝景点列表页面"""
        city_name = city_info.get('name', '未知城市') if city_info else '未知城市'
        city_id = city_info.get('city_id', 'unknown') if city_info else 'unknown'
        
        self.logger.info(f"开始爬取 {city_name} 的景点列表")
        try:
            # 初始化 Selenium WebDriver
            driver = webdriver.Edge(service=self.service, options=self.options)
            
            # 直接访问景点页面
            driver.get(url)
            
            # 增加初始等待时间
            time.sleep(random.uniform(5, 8))
            
            # 执行JavaScript来模拟真实浏览器
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            wait = WebDriverWait(driver, 30)
            
            # 持续爬取直到没有"后一页"按钮
            page_num = 1
            while True:
                self.logger.info(f"正在爬取 {city_name} 的第 {page_num} 页景点列表")
                
                # 等待景点列表加载
                selectors = [
                    "//div[@class='row-top']//li",
                    "//div[contains(@class, '_j_scenic_list')]//div[contains(@class, 'row-top')]//li",
                    "//div[contains(@class, 'scenic-list')]//li",
                    "//div[@class='_j_scenic_list']//li",
                    "//ul[contains(@class, 'scenic-list')]/li",
                    "//div[contains(@class, '_j_scenic_list')]//li"
                ]
                
                elements = None
                for selector in selectors:
                    try:
                        if len(driver.find_elements(By.XPATH, selector)) > 0:
                            elements = wait.until(
                                EC.presence_of_all_elements_located((By.XPATH, selector))
                            )
                            if elements:
                                self.logger.info(f"成功找到 {len(elements)} 个景点元素")
                                break
                    except Exception as e:
                        continue
                
                if not elements:
                    self.logger.error(f"未能找到 {city_name} 的任何景点元素")
                    # 保存页面源码以便调试
                    with open(f'results/page_source_error_{city_id}_p{page_num}.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    break
                
                # 处理当前页面的景点
                for attraction in elements:
                    try:
                        # 滚动到元素位置
                        driver.execute_script("arguments[0].scrollIntoView(true);", attraction)
                        time.sleep(0.5)
                        
                        # 获取景点信息
                        link_element = attraction.find_element(By.TAG_NAME, "a")
                        link = link_element.get_attribute("href")
                        name = attraction.find_element(By.TAG_NAME, "h3").text
                        
                        # 提取POI ID
                        poi_id = None
                        if "/poi/" in link:
                            poi_id = link.split("/poi/")[1].split(".html")[0]
                        
                        try:
                            score_element = attraction.find_element(By.CSS_SELECTOR, ".score")
                            if score_element:
                                score = score_element.text.strip()
                        except:
                            score = None
                            
                        try:
                            intro_element = attraction.find_element(By.CSS_SELECTOR, ".summary")
                            if intro_element:
                                intro = intro_element.text.strip()
                        except:
                            intro = None
                        
                        attraction_info = {
                            "name": name,
                            "link": link,
                            "poi_id": poi_id,
                            "score": score,
                            "intro": intro,
                            "city": city_name,
                            "city_id": city_id
                        }
                        
                        # 将景点详情页URL添加到Redis队列
                        if link and poi_id:
                            # 使用lpush将URL添加到队列
                            self.redis_client.lpush(f"{self.name}:detail_urls", link)
                            self.logger.info(f"已将景点详情页URL添加到队列: {link}")
                            
                            # 同时将基本信息存储到Redis
                            info_key = f"china:attraction:info:{poi_id}"
                            self.redis_client.set(info_key, json.dumps(attraction_info, ensure_ascii=False))
                        
                    except Exception as e:
                        self.logger.error(f"提取景点信息时出错: {str(e)}")
                        continue
                
                # 尝试翻页
                try:
                    # 查找"后一页"按钮
                    next_page = None
                    next_page_selectors = [
                        "//div[contains(@class, 'm-pagination')]/a[@title='后一页']",
                        "//div[contains(@class, 'paginator')]/a[text()='后一页']",
                        "/html/body/div[2]/div[5]/div/div[2]/div/a[text()='后一页']"
                    ]
                    
                    for selector in next_page_selectors:
                        elements = driver.find_elements(By.XPATH, selector)
                        if elements:
                            next_page = elements[0]
                            break
                    
                    # 如果找到了"后一页"按钮，点击
                    if next_page and next_page.is_enabled() and next_page.is_displayed():
                        # 滚动到按钮位置
                        driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
                        time.sleep(random.uniform(2, 3))
                        
                        # 尝试点击
                        try:
                            next_page.click()
                            page_num += 1
                            time.sleep(random.uniform(3, 5))
                        except Exception as click_error:
                            self.logger.error(f"点击'后一页'按钮失败: {str(click_error)}")
                            # 尝试使用JavaScript点击
                            driver.execute_script("arguments[0].click();", next_page)
                            page_num += 1
                            time.sleep(random.uniform(3, 5))
                    else:
                        self.logger.info(f"{city_name} 没有找到'后一页'按钮或按钮不可点击，爬取完成")
                        break
                except Exception as e:
                    self.logger.info(f"{city_name} 翻页出错，爬取完成: {str(e)}")
                    break
                
                # 限制最多爬取10页或200个景点
                if page_num > 10:
                    self.logger.info(f"{city_name} 已达到页数限制（页数: {page_num}），停止爬取")
                    break
            
            # 关闭driver
            driver.quit()
            
        except Exception as e:
            self.logger.error(f"爬取 {city_name} 景点列表时出错: {str(e)}")
            if 'driver' in locals():
                driver.quit()

    def process_detail_urls(self):
        """处理景点详情页URL队列"""
        # 从Redis队列中获取一个景点详情页URL
        url_data = self.redis_client.rpop(f"{self.name}:detail_urls")
        if url_data:
            try:
                # 尝试解析为JSON，如果失败则直接使用字符串
                try:
                    url_info = json.loads(url_data.decode('utf-8'))
                    url = url_info.get('url')
                    attraction_info = url_info.get('attraction_info')
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # 如果不是JSON格式，则直接使用字符串
                    url = url_data.decode('utf-8')
                    attraction_info = {'name': '未知景点', 'poi_id': None}
                    
                # 确保URL不为空
                if not url:
                    url = url_data.decode('utf-8')
                
                # 检查URL是否已经被处理过
                if not self.redis_client.sismember(f"{self.name}:detail:dupefilter", url):
                    self.logger.info(f"处理景点详情页: {url}")
                    # 将URL标记为已处理
                    self.redis_client.sadd(f"{self.name}:detail:dupefilter", url)
                    # 解析景点详情页
                    self.parse_attraction_detail(url, attraction_info)
                else:
                    self.logger.info(f"景点详情页已处理过: {url}")
            except Exception as e:
                self.logger.error(f"处理景点详情页URL时出错: {str(e)}")
                # 如果处理出错，将URL放回队列
                self.redis_client.lpush(f"{self.name}:detail_urls", url_data)
        else:
            self.logger.info("景点详情页URL队列为空")

    def parse_attraction_detail(self, url, attraction_info):
        """解析景点详情页面（使用Selenium）"""
        self.logger.info(f"正在爬取景点详情: {attraction_info.get('name', '未知景点')}")
        
        try:
            # 初始化 Selenium WebDriver
            driver = webdriver.Edge(service=self.service, options=self.options)
            
            # 访问景点详情页面
            driver.get(url)
            
            # 增加初始等待时间
            time.sleep(random.uniform(5, 8))
            
            # 执行JavaScript来模拟真实浏览器
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            wait = WebDriverWait(driver, 20)
            
            # 创建详情对象
            detail = {
                'name': attraction_info.get('name', '未知景点'),
                'poi_id': attraction_info.get('poi_id'),
                'link': url,
                'city': attraction_info.get('city', '未知城市'),
                'city_id': attraction_info.get('city_id')
            }
            
            # 提取景点名称（如果之前未获取）
            if detail['name'] == '未知景点' or detail['name'] == '待获取':
                try:
                    name_element = wait.until(
                        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "title")]/h1'))
                    )
                    detail['name'] = name_element.text.strip()
                except:
                    pass
            
            # 提取图片
            try:
                image_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "pic-big")]/img'))
                )
                detail['image'] = image_element.get_attribute('src')
            except:
                try:
                    image_element = driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[1]/div/a/div/div[1]/img')
                    detail['image'] = image_element.get_attribute('src')
                except:
                    detail['image'] = None
            
            # 提取简介
            try:
                summary_element = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'summary'))
                )
                detail['summary'] = summary_element.text.replace('\n', ' ').strip()
            except:
                detail['summary'] = None
            
            # 提取交通信息
            try:
                transport_element = driver.find_element(By.XPATH, '//dl[contains(.//dt, "交通")]/dd')
                detail['transport'] = transport_element.text.strip()
            except:
                detail['transport'] = None
            
            # 提取门票信息
            try:
                ticket_element = driver.find_element(By.XPATH, '//dl[contains(.//dt, "门票")]/dd')
                ticket_text = ticket_element.text.strip()
                # 处理门票信息，去除tips等
                ticket_lines = [line.strip() for line in ticket_text.split('\n') 
                              if line.strip() and not line.startswith('tips')]
                detail['ticket'] = ticket_lines[:2] if ticket_lines else None  # 取前两条有效信息
            except:
                detail['ticket'] = None
            
            # 提取开放时间
            try:
                opening_hours_element = driver.find_element(By.XPATH, '//dl[contains(.//dt, "开放时间")]/dd')
                detail['opening_hours'] = opening_hours_element.text.strip()
            except:
                detail['opening_hours'] = None
            
            # 提取位置信息
            try:
                location_element = driver.find_element(By.XPATH, '//div[contains(@class, "mod-location")]/div/p')
                detail['location'] = location_element.text.strip()
            except:
                detail['location'] = None
            
            # 提取评论
            detail['comments'] = []
            
            # 滚动到评论区域
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(random.uniform(2, 3))
                
                # 等待评论列表加载
                comment_selectors = [
                    '//div[contains(@class, "rev-list")]/ul/li',
                    '//ul[contains(@class, "rev-list")]/li',
                    '/html/body/div[2]/div[4]/div/div/div[4]/div[1]/ul/li'
                ]
                
                comment_elements = None
                for selector in comment_selectors:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        comment_elements = elements
                        break
                
                if comment_elements:
                    # 提取评论文本
                    for comment_element in comment_elements[:10]:  # 限制为前10条评论
                        try:
                            comment_text_element = comment_element.find_element(By.XPATH, './/p[contains(@class, "rev-txt")]')
                            comment_text = comment_text_element.text.strip()
                            if comment_text:
                                detail['comments'].append(comment_text)
                        except:
                            continue
            except Exception as e:
                self.logger.warning(f"提取评论时出错: {str(e)}")
            
            # 保存到Redis
            self.save_attraction_detail_to_redis(detail)
            
            # 关闭driver
            driver.quit()
            
        except Exception as e:
            self.logger.error(f"爬取景点详情时出错: {str(e)}")
            if 'driver' in locals():
                driver.quit()
    
    def save_attraction_detail_to_redis(self, detail):
        """将景点详情保存到Redis"""
        try:
            # 获取景点ID
            poi_id = detail.get('poi_id')
            if not poi_id:
                self.logger.error("景点ID为空，无法保存")
                return False
            
            # 添加时间戳和节点标识
            detail['crawl_time'] = int(time.time())
            detail['node_id'] = self.node_id
            
            # 使用管道和事务确保原子性操作
            pipe = self.redis_client.pipeline()
            
            # 检查是否已存在数据
            info_key = f"china:attraction:detail:{poi_id}"
            existing_data = self.redis_client.get(info_key)
            
            if existing_data:
                # 如果已存在数据，检查版本
                existing_detail = json.loads(existing_data.decode('utf-8'))
                existing_time = existing_detail.get('crawl_time', 0)
                
                # 只有新数据的时间戳更新，才更新数据
                if detail['crawl_time'] > existing_time:
                    self.logger.info(f"更新景点详情: {poi_id}, {detail.get('name', '未知景点')}")
                    # 将详情数据保存到Redis
                    pipe.set(info_key, json.dumps(detail, ensure_ascii=False))
                else:
                    self.logger.info(f"保留现有景点详情: {poi_id}, {existing_detail.get('name', '未知景点')}")
            else:
                self.logger.info(f"新增景点详情: {poi_id}, {detail.get('name', '未知景点')}")
                # 将详情数据保存到Redis
                pipe.set(info_key, json.dumps(detail, ensure_ascii=False))
            
            # 将景点ID添加到索引集合
            pipe.sadd("china:attractions:all", f"china:attraction:detail:{poi_id}")
            
            # 执行事务
            pipe.execute()
            
            return True
        except Exception as e:
            self.logger.error(f"保存景点详情到Redis失败: {str(e)}")
            return False

    def closed(self, reason):
        """爬虫关闭时的回调函数"""
        self.logger.info(f"爬虫关闭，原因: {reason}")
        
        # 停止定期保存检查点的线程
        self.stop_checkpoint_thread = True
        if hasattr(self, 'checkpoint_thread') and self.checkpoint_thread.is_alive():
            self.checkpoint_thread.join(timeout=5)
            self.logger.info("已停止定期保存检查点线程")
        
        # 保存断点续爬检查点
        self.save_checkpoint()
        
        # 记录爬虫结束状态
        self.save_spider_status(f"closed: {reason}")
        
        # 计算运行时间
        end_time = datetime.now()
        run_time = end_time - self.start_time
        self.logger.info(f"爬虫运行时间: {run_time}")
        
        # 记录爬取统计信息
        try:
            cities_processed = self.redis_client.scard(f"{self.name}:cities:dupefilter")
            list_processed = self.redis_client.scard(f"{self.name}:list:dupefilter")
            detail_processed = self.redis_client.scard(f"{self.name}:detail:dupefilter")
            
            city_count = len(self.redis_client.keys("china:city:info:*"))
            attraction_count = self.redis_client.scard("china:attractions:all")
            
            self.logger.info(f"爬取统计: 处理城市页面 {cities_processed} 个，处理列表页面 {list_processed} 个，处理详情页面 {detail_processed} 个")
            self.logger.info(f"数据统计: 保存城市 {city_count} 个，保存景点 {attraction_count} 个")
            
            # 导出Redis中的景点数据到JSON文件
            self.export_attractions_to_json()
            
        except Exception as e:
            self.logger.error(f"记录爬取统计信息失败: {str(e)}")
    
    def export_attractions_to_json(self):
        """将Redis中的景点数据导出到JSON文件"""
        try:
            # 获取所有景点的键
            attraction_keys = self.redis_client.smembers("china:attractions:all")
            
            if not attraction_keys:
                self.logger.warning("未找到任何景点数据，无法导出")
                return
            
            # 从Redis中获取所有景点数据
            attractions = []
            for key in attraction_keys:
                data = self.redis_client.get(key)
                if data:
                    try:
                        attraction = json.loads(data)
                        attractions.append(attraction)
                    except json.JSONDecodeError:
                        self.logger.error(f"景点数据格式错误: {key}")
            
            # 确保输出目录存在
            os.makedirs('results', exist_ok=True)
            
            # 将数据写入JSON文件
            output_file = 'attractions_distributed.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(attractions, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"已将 {len(attractions)} 个景点数据导出到 {output_file}")
        except Exception as e:
            self.logger.error(f"导出景点数据到JSON文件失败: {str(e)}")

# 如果直接运行此文件，则启动爬虫
if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(ChinaAttractionsDBSpider)
    process.start() 