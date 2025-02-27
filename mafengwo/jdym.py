#**
# 使用selenium爬取马蜂窝景点页面
# 初始url为：https://www.mafengwo.cn/jd/10065/gonglve.html
""" 这个标签下/html/body/div[2]/div[5]/div/div[1]/ul有很多li标签
li标签的元素结构如下：
<li>
        <a href="/poi/3474.html" target="_blank" title="故宫">
            <div class="img"><img src="https://p1-q.mafengwo.net/s19/M00/2D/FE/CoNFJmJXiTI2MiNEAAkbC7NyIs4.jpeg?imageMogr2%2Fthumbnail%2F%21192x130r%2Fgravity%2FCenter%2Fcrop%2F%21192x130%2Fquality%2F100" width="192" height="130"></div>
            <h3>故宫</h3>
        </a>
</li>
需要获取这些li标签中的景点详情页面链接（href="/poi/3474.html"）和景点名（<h3>故宫</h3>） """
#**

import random
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

class MafengwoSpider:
    def __init__(self):
        # 初始化浏览器选项
        self.options = webdriver.EdgeOptions()
        
        # 临时注释掉无头模式来测试
        # self.options.add_argument('--headless')
        
        # 添加其他参数以避免检测
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        
        # 添加更真实的浏览器特征
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # 使用更真实的 User-Agent
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0')
        
        # 添加忽略证书错误的选项
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 禁用日志
        
        # 添加 WebGL 相关参数
        self.options.add_argument('--enable-unsafe-swiftshader')
        self.options.add_argument('--disable-software-rasterizer')
        
        # 添加代理设置（如果需要）
        # self.options.add_argument('--proxy-server=http://your-proxy-address:port')
        
        # 创建Service对象
        service = Service(executable_path="E:\\edgedriver\\msedgedriver.exe")
        
        # 使用Service对象初始化驱动
        self.driver = webdriver.Edge(
            service=service,
            options=self.options
        )
        self.base_url = "https://www.mafengwo.cn/jd/10065/gonglve.html"
        self.results = []

    def get_attractions(self):
        try:
            self.driver.get(self.base_url)
            print("成功访问页面")
            
            # 增加初始等待时间
            time.sleep(random.uniform(3, 5))
            
            # 执行JavaScript来模拟真实浏览器
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 尝试等待页面完全加载
            wait = WebDriverWait(self.driver, 30)  # 增加等待时间到30秒
            
            # 保存页面源码以便调试
            print("当前页面源码已保存")
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            print("正在分析页面结构...")
            
            # 尝试新的选择器
            selectors = [
                "//div[@class='row-top']//li",  # 新增选择器
                "//div[contains(@class, '_j_scenic_list')]//div[contains(@class, 'row-top')]//li",  # 新增选择器
                "//div[contains(@class, 'scenic-list')]//li",
                "//div[@class='_j_scenic_list']//li",
                "//ul[contains(@class, 'scenic-list')]/li",
                "//div[contains(@class, '_j_scenic_list')]//li"
            ]
            
            elements = None
            for selector in selectors:
                try:
                    print(f"尝试选择器: {selector}")
                    # 先检查元素是否存在
                    if len(self.driver.find_elements(By.XPATH, selector)) > 0:
                        print(f"找到匹配元素，等待加载...")
                        elements = wait.until(
                            EC.presence_of_all_elements_located((By.XPATH, selector))
                        )
                        if elements:
                            print(f"成功找到 {len(elements)} 个元素")
                            break
                except Exception as e:
                    print(f"选择器 {selector} 失败: {str(e)}")
                    continue
                
            if not elements:
                # 尝试打印页面标题和URL
                print(f"页面标题: {self.driver.title}")
                print(f"当前URL: {self.driver.current_url}")
                # 检查是否被重定向到登录页面
                if "login" in self.driver.current_url.lower():
                    raise Exception("被重定向到登录页面，可能需要登录")
                raise Exception("未能找到任何景点元素")
            
            for attraction in elements:
                try:
                    # 使用 JavaScript 滚动到元素位置
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", attraction)
                    time.sleep(0.5)  # 短暂延迟等待元素加载
                    
                    # 获取景点链接和名称
                    link = attraction.find_element(By.TAG_NAME, "a").get_attribute("href")
                    name = attraction.find_element(By.TAG_NAME, "h3").text
                    
                    print(f"正在处理景点: {name}")
                    
                    # 提取POI ID
                    poi_id = link.split("/poi/")[1].split(".html")[0]
                    
                    attraction_info = {
                        "name": name,
                        "link": link,
                        "poi_id": poi_id
                    }
                    
                    self.results.append(attraction_info)
                    
                except Exception as e:
                    print(f"提取景点信息时出错: {str(e)}")
                    continue
            
            # 保存结果到JSON文件
            self.save_results()
            
        except Exception as e:
            print(f"详细错误信息: {str(e)}")
            print(f"当前页面URL: {self.driver.current_url}")
            # 保存页面源码以供调试
            with open('error_page.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            raise
        finally:
            self.driver.quit()

    def save_results(self):
        """保存结果到JSON文件"""
        with open('attractions.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"成功保存{len(self.results)}个景点信息到attractions.json")



    def run(self):
        """运行爬虫"""
        print("开始爬取马蜂窝景点信息...")
        self.get_attractions()
        print("爬取完成！")

if __name__ == "__main__":
    spider = MafengwoSpider()
    spider.run()
