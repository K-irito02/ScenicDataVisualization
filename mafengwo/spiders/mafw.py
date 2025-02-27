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
        
        # 更新 User-Agent
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

    # 解析马蜂窝目的地页面
    def parse(self, response):
        # 添加日志来查看响应状态
        self.logger.info(f'Response status: {response.status}')
        self.logger.info(f'Response URL: {response.url}')
        
        base_xpath = '/html/body/div[2]/div[2]/div/div[3]/div[1]'
        provinces = []
        
        # 处理直辖市
        municipalities_dl = response.xpath(f'{base_xpath}/div[1]/dl[1]')
        if municipalities_dl:
            # 获取"直辖市"标题
            title = municipalities_dl.xpath('./dt/text()').get()
            # 获取直辖市的链接
            municipality_links = municipalities_dl.xpath('./dd/a/@href').getall()
            municipality_names = municipalities_dl.xpath('./dd/a/text()').getall()
            
            # 将直辖市信息添加到结果中
            for name, link in zip(municipality_names, municipality_links):
                # 修改链接格式
                if 'travel-scenic-spot/mafengwo' in link:
                    # 提取ID
                    id = link.split('/')[-1].replace('.html', '')
                    # 构建新的链接
                    link = f'/jd/{id}/gonglve.html'
                provinces.append({
                    'type': '直辖市',
                    'name': name,
                    'link': response.urljoin(link)
                })
        
        # 处理其他省份（在dt标签中的省份）
        for div_index in [1, 2]:  # 遍历两个div
            province_dls = response.xpath(f'{base_xpath}/div[{div_index}]/dl[position()>1]')  # 跳过直辖市的dl
            for dl in province_dls:
                # 获取dt中的所有省份链接和名称
                province_links = dl.xpath('./dt/a/@href').getall()
                province_names = dl.xpath('./dt/a/text()').getall()
                
                # 将省份信息添加到结果中
                for name, link in zip(province_names, province_links):
                    # 修改链接格式
                    if 'travel-scenic-spot/mafengwo' in link:
                        # 提取ID
                        id = link.split('/')[-1].replace('.html', '')
                        # 构建新的链接
                        link = f'/jd/{id}/gonglve.html'
                    provinces.append({
                        'type': '省份',
                        'name': name,
                        'link': response.urljoin(link)
                    })
        
        # 打印结果并处理省份链接
        for province in provinces:
            print(f"类型: {province['type']}, 省份: {province['name']}, 链接: {province['link']}")
            # 对于直辖市且名称为北京的情况，发送请求获取景点信息
            if province['type'] == '直辖市' and province['name'] == '北京':
                # 添加随机延迟
                time.sleep(random.uniform(1, 3))
                yield scrapy.Request(
                    url=province['link'],
                    callback=self.parse_attractions,
                    meta={'province_info': province},
                    dont_filter=True
                )

    def parse_attractions(self, response):
        """使用selenium爬取马蜂窝景点页面"""
        try:
            # 初始化 Selenium WebDriver
            driver = webdriver.Edge(service=self.service, options=self.options)
            
            # 访问景点页面
            attractions_url = response.meta['province_info']['link']
            driver.get(attractions_url)
            
            # 增加初始等待时间
            time.sleep(random.uniform(3, 5))
            
            # 执行JavaScript来模拟真实浏览器
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            wait = WebDriverWait(driver, 30)
            
            # 持续爬取直到没有"后一页"按钮
            while True:
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
                                self.logger.info(f"成功找到 {len(elements)} 个元素")
                                break
                    except Exception as e:
                        continue
                
                if not elements:
                    self.logger.error("未能找到任何景点元素")
                    break
                
                # 处理当前页面的景点
                for attraction in elements:
                    try:
                        # 滚动到元素位置
                        driver.execute_script("arguments[0].scrollIntoView(true);", attraction)
                        time.sleep(0.5)
                        
                        # 获取景点信息
                        link = attraction.find_element(By.TAG_NAME, "a").get_attribute("href")
                        name = attraction.find_element(By.TAG_NAME, "h3").text
                        poi_id = link.split("/poi/")[1].split(".html")[0]
                        
                        attraction_info = {
                            "name": name,
                            "link": link,
                            "poi_id": poi_id
                        }
                        
                        self.results.append(attraction_info)
                        yield attraction_info
                        
                    except Exception as e:
                        self.logger.error(f"提取景点信息时出错: {str(e)}")
                        continue
                
                try:
                    # 查找"后一页"按钮 - 使用更可靠的定位方式
                    next_page = wait.until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[5]/div/div[2]/div/a[text()='后一页']"))
                    )
                    
                    # 检查"后一页"按钮是否可点击和可见
                    if next_page.is_enabled() and next_page.is_displayed():
                        # 滚动到按钮位置
                        driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
                        time.sleep(random.uniform(1, 2))
                        
                        # 尝试点击
                        try:
                            next_page.click()
                            time.sleep(random.uniform(2, 3))
                        except Exception as click_error:
                            self.logger.error(f"点击'后一页'按钮失败: {str(click_error)}")
                            # 尝试使用JavaScript点击
                            driver.execute_script("arguments[0].click();", next_page)
                            time.sleep(random.uniform(2, 3))
                    else:
                        self.logger.info("找到'后一页'按钮，但不可点击，爬取完成")
                        break
                except Exception as e:
                    self.logger.info("没有找到'后一页'按钮，爬取完成")
                    break
                
            # 保存结果到JSON文件
            with open('attractions.json', 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            self.logger.info(f"成功保存{len(self.results)}个景点信息到attractions.json")
            
        except Exception as e:
            self.logger.error(f"详细错误信息: {str(e)}")
            # 保存错误页面源码
            with open('error_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
        finally:
            driver.quit()