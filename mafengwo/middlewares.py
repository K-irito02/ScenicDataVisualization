# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from random import choice
from mafengwo.settings import USER_AGENT_LIST, PROXY_LIST
from selenium import webdriver
from selenium.webdriver.edge.service import Service
import time
from scrapy.http import HtmlResponse
from scrapy import signals
from selenium.webdriver.common.by import By

class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        request.headers['User-Agent'] = choice(USER_AGENT_LIST)

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        proxy = choice(PROXY_LIST)
        # 确保代理地址包含协议
        if not proxy['ip_port'].startswith(('http://', 'https://')):
            request.meta['proxy'] = f"http://{proxy['ip_port']}"
        else:
            request.meta['proxy'] = proxy['ip_port']

class SeleniumMiddleware(object):   
    def process_request(self, request, spider):
        url = request.url

        if "mdd" in url:
            # 使用 Service 类来指定驱动路径
            service = Service(executable_path=r"E:\\edgedriver\\msedgedriver.exe")
            driver = webdriver.Edge(service=service)
            driver.get(url)
            time.sleep(5)
            driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/a[1]").click()
            time.sleep(2)
            html = driver.page_source
            
            driver.close()
            # 创建响应对象
            res = HtmlResponse(url=url, body=html, encoding='utf-8', request=request)
            
            return res
        

