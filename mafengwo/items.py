# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MafengwoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 国内(省份或直辖市)
    internal = scrapy.Field()
    # 国内(省份或直辖市)的链接
    internal_link = scrapy.Field()
    # 景区名
    spotName = scrapy.Field()
    # 景区名链接
    spotName_link = scrapy.Field()
    # 景点位置
    location = scrapy.Field()
    # 简介
    introduction = scrapy.Field()
    # 交通
    transportation = scrapy.Field()
    # 门票
    ticket = scrapy.Field()
    # 开放时间
    opening_time = scrapy.Field()
    # 评论数量
    number_of_reviews = scrapy.Field()
    # 用户评论
    user_comments = scrapy.Field()

    pass
