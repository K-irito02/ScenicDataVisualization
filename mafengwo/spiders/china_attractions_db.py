import scrapy
import random
import time
import json
import os
import redis
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

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

    def __init__(self, node_id='node1', is_master=False, task_type='all', redis_host='localhost', *args, **kwargs):
        super(ChinaAttractionsDBSpider, self).__init__(*args, **kwargs)
        self.node_id = node_id
        self.is_master = is_master
        self.task_type = task_type  # 'all', 'cities', 'list', 'detail'
        
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
            if is_master:
                self.redis_client.delete(f"{self.name}:cities_urls")
                self.redis_client.delete(f"{self.name}:list_urls")
                self.redis_client.delete(f"{self.name}:detail_urls")
                self.redis_client.lpush(f"{self.name}:cities_urls", "https://www.mafengwo.cn/mdd/")
                self.logger.info("主节点已初始化URL队列")
        except Exception as e:
            self.logger.error(f"Redis连接初始化失败: {str(e)}")
            self.redis_client = None

    def start_requests(self):
        """根据任务类型处理不同的URL队列"""
        if self.task_type == 'all' or self.task_type == 'cities':
            self.process_cities_urls()
        
        if self.task_type == 'all' or self.task_type == 'list':
            self.process_list_urls()
        
        if self.task_type == 'all' or self.task_type == 'detail':
            self.process_detail_urls()
        
        return []

    def process_cities_urls(self):
        """处理城市列表页URL队列"""
        self.logger.info("开始处理城市列表页URL队列")
        
        # 从Redis队列中获取所有城市列表页URL
        while True:
            cities_url = self.redis_client.rpop(f"{self.name}:cities_urls")
            if not cities_url:
                self.logger.info("城市列表页URL队列为空，处理完成")
                break
                
            if isinstance(cities_url, bytes):
                cities_url = cities_url.decode('utf-8')
                
            self.logger.info(f"处理城市列表页URL: {cities_url}")
            self.parse_cities_list(cities_url)

    def parse_cities_list(self, url):
        """使用selenium爬取马蜂窝城市列表页面"""
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
            
            # 等待城市列表加载
            city_selectors = [
                "//div[contains(@class, 'hot-list')]//div[contains(@class, 'item')]",
                "//div[contains(@class, 'hot-list')]//li",
                "//div[contains(@class, 'hot-list')]//a"
            ]
            
            city_elements = None
            for selector in city_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements and len(elements) > 0:
                        city_elements = elements
                        self.logger.info(f"成功找到 {len(elements)} 个城市元素")
                        break
                except Exception as e:
                    continue
            
            if not city_elements:
                self.logger.error("未能找到任何城市元素")
                # 保存页面源码以便调试
                with open(f'results/cities_page_source_error.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                driver.quit()
                return
            
            # 处理城市列表
            for city_element in city_elements:
                try:
                    # 滚动到元素位置
                    driver.execute_script("arguments[0].scrollIntoView(true);", city_element)
                    time.sleep(0.5)
                    
                    # 获取城市信息
                    link_element = city_element.find_element(By.TAG_NAME, "a")
                    link = link_element.get_attribute("href")
                    name = link_element.text.strip()
                    
                    # 提取城市ID
                    city_id = None
                    if "/travel-scenic-spot/mafengwo/" in link:
                        city_id = link.split("/travel-scenic-spot/mafengwo/")[1].split(".html")[0]
                    
                    if not city_id or not name:
                        continue
                    
                    # 构建景点列表页URL
                    attractions_list_url = f"https://www.mafengwo.cn/jd/{city_id}/gonglve.html"
                    
                    city_info = {
                        "name": name,
                        "link": link,
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
                    self.logger.error(f"提取城市信息时出错: {str(e)}")
                    continue
            
            # 关闭driver
            driver.quit()
            
        except Exception as e:
            self.logger.error(f"爬取城市列表时出错: {str(e)}")
            if 'driver' in locals():
                driver.quit()

    def process_list_urls(self):
        """处理景点列表页URL队列"""
        self.logger.info("开始处理景点列表页URL队列")
        
        # 从Redis队列中获取所有列表页URL
        while True:
            list_url = self.redis_client.rpop(f"{self.name}:list_urls")
            if not list_url:
                self.logger.info("景点列表页URL队列为空，处理完成")
                break
                
            if isinstance(list_url, bytes):
                list_url = list_url.decode('utf-8')
                
            self.logger.info(f"处理景点列表页URL: {list_url}")
            
            # 提取城市ID
            city_id = None
            if "/jd/" in list_url:
                city_id = list_url.split("/jd/")[1].split("/")[0]
            
            # 获取城市信息
            city_info = None
            if city_id:
                info_key = f"china:city:info:{city_id}"
                city_info_json = self.redis_client.get(info_key)
                if city_info_json:
                    if isinstance(city_info_json, bytes):
                        city_info_json = city_info_json.decode('utf-8')
                    city_info = json.loads(city_info_json)
            
            self.parse_attractions_list(list_url, city_info)

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
        """处理详情页URL队列"""
        self.logger.info("开始处理详情页URL队列")
        
        # 从Redis队列中获取所有详情页URL
        while True:
            detail_url = self.redis_client.rpop(f"{self.name}:detail_urls")
            if not detail_url:
                self.logger.info("详情页URL队列为空，处理完成")
                break
                
            if isinstance(detail_url, bytes):
                detail_url = detail_url.decode('utf-8')
                
            # 提取POI ID
            poi_id = None
            if "/poi/" in detail_url:
                poi_id = detail_url.split("/poi/")[1].split(".html")[0]
            
            # 获取基本信息
            info_key = f"china:attraction:info:{poi_id}"
            attraction_info_json = self.redis_client.get(info_key)
            
            if attraction_info_json:
                if isinstance(attraction_info_json, bytes):
                    attraction_info_json = attraction_info_json.decode('utf-8')
                attraction_info = json.loads(attraction_info_json)
            else:
                attraction_info = {
                    "link": detail_url,
                    "poi_id": poi_id,
                    "name": "待获取",
                    "city": "未知城市"
                }
                
            self.logger.info(f"处理详情页URL: {detail_url}, 景点: {attraction_info.get('name', '未知景点')}")
            self.parse_attraction_detail(detail_url, attraction_info)

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
        """保存景点详情到Redis数据库"""
        if not self.redis_client:
            self.logger.error("Redis客户端未初始化，无法保存数据")
            return
        
        try:
            # 生成唯一键
            city_id = detail.get('city_id', 'unknown')
            key = f"china:attraction:{detail.get('poi_id', hash(detail['name']))}"
            
            # 将详情转换为JSON字符串
            detail_json = json.dumps(detail, ensure_ascii=False)
            
            # 存储到Redis
            self.redis_client.set(key, detail_json)
            
            # 添加到索引列表
            self.redis_client.sadd("china:attractions:all", key)
            
            # 添加到城市索引列表
            self.redis_client.sadd(f"china:city:{city_id}:attractions", key)
            
            self.logger.info(f"已保存景点详情到Redis: {detail['name']}")
        except Exception as e:
            self.logger.error(f"保存景点详情到Redis失败: {str(e)}")

# 如果直接运行此文件，则启动爬虫
if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(ChinaAttractionsDBSpider)
    process.start() 