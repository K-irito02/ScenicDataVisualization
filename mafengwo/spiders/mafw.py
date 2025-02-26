import scrapy
import random
import time


class MfwSpider(scrapy.Spider):
    name = "mafw"
    allowed_domains = ["mafengwo.cn"]  # 修改为马蜂窝域名
    start_urls = ["https://www.mafengwo.cn/mdd/"]  # 修改为https

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
                    provinces.append({
                        'type': '省份',
                        'name': name,
                        'link': response.urljoin(link)
                    })
        
        # 打印结果
        for province in provinces:
            print(f"类型: {province['type']}, 省份: {province['name']}, 链接: {province['link']}")
            
