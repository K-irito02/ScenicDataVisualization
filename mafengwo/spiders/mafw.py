import scrapy
import random
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os


class MfwSpider(scrapy.Spider):
    name = "mafw"
    allowed_domains = ["mafengwo.cn"]  # 修改为马蜂窝域名
    start_urls = ["https://www.mafengwo.cn/mdd/"]  # 修改为https

    def __init__(self, *args, **kwargs):
        super(MfwSpider, self).__init__(*args, **kwargs)
        # 初始化 Selenium 相关配置
        self.options = webdriver.EdgeOptions()
        
        # 添加浏览器参数
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--enable-unsafe-swiftshader')
        self.options.add_argument('--disable-software-rasterizer')
        
        # 创建Service对象
        self.service = Service(executable_path="E:\\edgedriver\\msedgedriver.exe")
        self.results = []

    def start_requests(self):
        url = self.start_urls[0]
        
        # 更新User-Agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.mafengwo.cn/'
        }
        
        # 更新Cookie
        cookies = {
            'mfw_uuid': '67a9f3ee-ec55-051a-0b8f-6d0fa67058fd',
            'uva': 's%3A92%3A%22a%3A3%3A%7Bs%3A2%3A%22lt%22%3Bi%3A1739191278%3Bs%3A10%3A%22last_refer%22%3Bs%3A24%3A%22https%3A%2F%2Fwww.mafengwo.cn%2F%22%3Bs%3A5%3A%22rhost%22%3BN%3B%7D%22%3B',
            '__mfwurd': 'a%3A3%3A%7Bs%3A6%3A%22f_time%22%3Bi%3A1739191278%3Bs%3A9%3A%22f_rdomain%22%3Bs%3A15%3A%22www.mafengwo.cn%22%3Bs%3A6%3A%22f_host%22%3Bs%3A3%3A%22www%22%3B%7D',
            '__mfwuuid': '67a9f3ee-ec55-051a-0b8f-6d0fa67058fd',
            'oad_n': 'a%3A3%3A%7Bs%3A3%3A%22oid%22%3Bi%3A1029%3Bs%3A2%3A%22dm%22%3Bs%3A15%3A%22www.mafengwo.cn%22%3Bs%3A2%3A%22ft%22%3Bs%3A19%3A%222025-02-22+12%3A51%3A55%22%3B%7D',
            '__mfwc': 'direct',
            '__omc_chl': '',
            '__omc_r': '',
            'PHPSESSID': 'ksgt7n0qvse53mifkfmq8865m0',
            'bottom_ad_status': '0',
            '__mfwa': '1739191280787.86947.9.1740488152961.1740492735048',
            '__mfwlv': '1740492735',
            '__mfwvn': '8',
            '__mfwb': 'bae22ef5d442.3.direct',
            '__mfwlt': '1740492785',
            'w_tsfp': 'ltvuV0MF2utBvS0Q7artnUmmFz0jdT84h0wpEaR0f5thQLErU5mB0YJzvMP2N3Te68xnvd7DsZoyJTLYCJI3dwNGE8SQe4pH3w/EwYdz2okUCEUyFZ+IWgFLdbkh62ZAfHhCNxS00jA8eIUd379yilkMsyN1zap3TO14fstJ019E6KDQmI5uDW3HlFWQRzaLbjcMcuqPr6g18L5a5TmO4l6oL1t8VelDhkyb1X1NB3En4UfpfepYYxj4Jcj9SqA='
        }

        # 添加随机延迟
        time.sleep(random.uniform(1, 3))
        
        yield scrapy.Request(
            url=url,
            headers=headers,
            cookies=cookies,
            callback=self.parse,
            dont_filter=True  # 防止重定向被过滤
        )
        
        # 测试景点详情页解析
        # 直接访问一个景点详情页进行测试
        test_poi_url = "https://www.mafengwo.cn/poi/4131.html"  # 爨底下村景点页面
        yield scrapy.Request(
            url=test_poi_url,
            headers=headers,
            cookies=cookies,
            callback=self.parse_poi_detail,
            dont_filter=True
        )
    
    def parse(self, response):
        # 原有的解析逻辑
        # ... 这里可以添加获取景点列表的代码
        self.logger.info(f"正在解析页面: {response.url}")
        
        # 这里可以添加提取景点链接的代码
        # poi_links = response.xpath('//a[contains(@href, "/poi/")]/@href').getall()
        # for link in poi_links:
        #     full_url = response.urljoin(link)
        #     yield scrapy.Request(full_url, callback=self.parse_poi_detail)
    
    def parse_poi_detail(self, response):
        """解析景点详情页面"""
        self.logger.info(f"正在解析景点详情页: {response.url}")
        
        # 提取景点ID
        poi_id = response.url.split('/')[-1].split('.')[0]
        
        # 提取景点名称
        poi_name = response.xpath('//div[@class="title"]/h1/text()').get()
        
        # 提取景点图片
        poi_image = response.xpath('/html/body/div[2]/div[3]/div[1]/div/a/div/div[1]/img/@src').get()
        
        # 提取景点简介
        poi_summary = response.xpath('//div[@class="summary"]/text()').getall()
        poi_summary = ''.join([s.strip() for s in poi_summary if s.strip()])
        
        # 提取交通信息
        poi_traffic = response.xpath('/html/body/div[2]/div[3]/div[2]/dl[1]/dd//text()').getall()
        poi_traffic = ''.join([t.strip() for t in poi_traffic if t.strip()])
        
        # 提取门票信息
        poi_ticket = response.xpath('/html/body/div[2]/div[3]/div[2]/dl[2]/dd/div[1]/div//text()').getall()
        poi_ticket = ''.join([t.strip() for t in poi_ticket if t.strip()])
        
        # 提取开放时间
        poi_opening_hours = response.xpath('/html/body/div[2]/div[3]/div[2]/dl[3]/dd//text()').getall()
        poi_opening_hours = ''.join([h.strip() for h in poi_opening_hours if h.strip()])
        
        # 提取景点位置
        poi_location = response.xpath('/html/body/div[2]/div[3]/div[3]/div[1]/p/text()').get()
        
        # 提取评论数量
        poi_comment_count = response.xpath('/html/body/div[2]/div[4]/div/div/div[1]/span/em/text()').get()
        if poi_comment_count:
            poi_comment_count = int(poi_comment_count)
        else:
            poi_comment_count = 0
        
        # 构建景点信息字典
        poi_info = {
            'id': poi_id,
            'name': poi_name,
            'image': poi_image,
            'summary': poi_summary,
            'traffic': poi_traffic,
            'ticket': poi_ticket,
            'opening_hours': poi_opening_hours,
            'location': poi_location,
            'comment_count': poi_comment_count,
            'url': response.url
        }
        
        self.logger.info(f"已提取景点信息: {poi_name}")
        
        # 将结果添加到列表中
        self.results.append(poi_info)
        
        # 每次获取数据后就保存
        with open('attractions_01.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)
        
        # 也可以使用yield返回Item
        yield poi_info
    
    def closed(self, reason):
        """爬虫关闭时将结果保存到JSON文件"""
        if self.results:
            # 使用绝对路径
            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'attractions_01.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=4)
            self.logger.info(f"已保存{len(self.results)}个景点信息到{file_path}")



