from django.db import models

# Create your models here.

class ScenicData(models.Model):
    """景区数据模型"""
    scenic_id = models.CharField(max_length=20, primary_key=True, db_column='景区ID', verbose_name='景区ID')
    name = models.CharField(max_length=100, db_column='景区名称', verbose_name='景区名称')
    image_url = models.URLField(max_length=500, null=True, blank=True, db_column='图片URL', verbose_name='图片URL')
    description = models.TextField(null=True, blank=True, db_column='景区简介', verbose_name='景区简介')
    province = models.CharField(max_length=50, null=True, blank=True, db_column='所在省份', verbose_name='所在省份')
    city = models.CharField(max_length=50, null=True, blank=True, db_column='所在城市', verbose_name='所在城市')
    district = models.CharField(max_length=50, null=True, blank=True, db_column='所在区县', verbose_name='所在区县')
    street = models.CharField(max_length=100, null=True, blank=True, db_column='所在街道镇乡', verbose_name='所在街道镇乡')
    coordinates = models.CharField(max_length=50, null=True, blank=True, db_column='经纬度', verbose_name='经纬度')
    scenic_type = models.CharField(max_length=200, null=True, blank=True, db_column='景区类型及级别', verbose_name='景区类型及级别')
    opening_hours = models.TextField(null=True, blank=True, db_column='开放时间原数据', verbose_name='开放时间原数据')
    ticket_price = models.TextField(null=True, blank=True, db_column='票价原数据', verbose_name='票价原数据')
    transportation = models.TextField(null=True, blank=True, db_column='交通原数据', verbose_name='交通原数据')
    comments = models.TextField(null=True, blank=True, db_column='评论原数据', verbose_name='评论原数据')
    min_price = models.CharField(max_length=50, null=True, blank=True, db_column='最低票价', verbose_name='最低票价')
    # 该列已从数据库中删除，注释掉避免出错
    # transport_mode = models.CharField(max_length=255, null=True, blank=True, db_column='交通方式', verbose_name='交通方式')
    comment_count = models.IntegerField(null=True, blank=True, db_column='评论数量', verbose_name='评论数量')
    sentiment = models.CharField(max_length=10, null=True, blank=True, db_column='情感倾向', verbose_name='情感倾向')
    sentiment_score = models.FloatField(null=True, blank=True, db_column='情感得分', verbose_name='情感得分')
    sentiment_magnitude = models.FloatField(null=True, blank=True, db_column='情感强度', verbose_name='情感强度')
    high_frequency_words = models.TextField(null=True, blank=True, db_column='高频词', verbose_name='高频词')
    update_time = models.DateTimeField(auto_now=True, db_column='更新时间', verbose_name='更新时间')
    
    class Meta:
        db_table = 'summary_table'
        verbose_name = '景区数据'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name

class PriceData(models.Model):
    """景区票价数据模型"""
    scenic_name = models.CharField(max_length=100, verbose_name='景区名称')
    city_name = models.CharField(max_length=50, verbose_name='所在省份')
    ticket = models.CharField(max_length=200, blank=True, null=True, verbose_name='景区的门票价格')
    
    def __str__(self):
        return self.scenic_name
    
    class Meta:
        verbose_name = '景区票价数据'
        verbose_name_plural = '景区票价数据'
        db_table = 'price_process_django'  # 修改表名避免冲突

class ProvinceTraffic(models.Model):
    """省份交通数据模型"""
    province = models.CharField(max_length=50, verbose_name='省份名')
    transport_frequency = models.TextField(blank=True, null=True, verbose_name='交通方式类型出现次数')
    transport_count = models.IntegerField(blank=True, null=True, verbose_name='交通方式类型数量')
    
    def __str__(self):
        return self.province
    
    class Meta:
        verbose_name = '省份交通数据'
        verbose_name_plural = '省份交通数据'
        db_table = 'province_traffic'  # 直接使用已有数据表

class TimeData(models.Model):
    """景区开放时间数据模型"""
    id = models.CharField(max_length=20, primary_key=True, blank=True, verbose_name='景区ID')
    scenic_name = models.CharField(max_length=100, verbose_name='景区名')
    city_name = models.CharField(max_length=50, verbose_name='城市名')
    time_range = models.CharField(max_length=200, null=True, blank=True, verbose_name='开放时间段')
    date_range = models.CharField(max_length=200, null=True, blank=True, verbose_name='日期范围')
    weekdays = models.CharField(max_length=100, null=True, blank=True, verbose_name='适用工作日')
    season = models.CharField(max_length=50, null=True, blank=True, verbose_name='季节')
    is_holiday = models.BooleanField(default=False, null=True, blank=True, verbose_name='是否节假日')
    is_closed = models.BooleanField(default=False, null=True, blank=True, verbose_name='是否关闭')
    is_24h = models.BooleanField(default=False, null=True, blank=True, verbose_name='是否24小时开放')
    stop_ticket_time = models.CharField(max_length=50, null=True, blank=True, verbose_name='停止售票时间')
    
    def __str__(self):
        return self.scenic_name
    
    class Meta:
        verbose_name = '景区开放时间数据'
        verbose_name_plural = '景区开放时间数据'
        db_table = 'time_process'  # 直接使用已有数据表

class TrafficData(models.Model):
    """交通数据模型"""
    transport = models.CharField(max_length=50, verbose_name='交通类型')
    transport_count = models.IntegerField(blank=True, null=True, verbose_name='交通类型出现次数')
    
    def __str__(self):
        return self.transport
    
    class Meta:
        verbose_name = '交通数据'
        verbose_name_plural = '交通数据'
        db_table = 'traffic_add'  # 直接使用已有数据表

class HierarchyTicketBase(models.Model):
    """层级票价基础模型（抽象类）"""
    level = models.CharField(max_length=50, primary_key=True, verbose_name='等级名称')
    count = models.IntegerField(verbose_name='该等级的景区数量')
    average_price = models.FloatField(blank=True, null=True, verbose_name='平均票价')
    min_price = models.FloatField(blank=True, null=True, verbose_name='最低票价')
    max_price = models.FloatField(blank=True, null=True, verbose_name='最高票价')
    median_price = models.FloatField(blank=True, null=True, verbose_name='中位数票价')
    
    class Meta:
        abstract = True

class ScenicLevelPrice(HierarchyTicketBase):
    """景区等级与门票价格关系"""
    class Meta:
        verbose_name = '景区等级票价'
        verbose_name_plural = '景区等级票价'
        db_table = 'scenic_level_price'
        managed = True

class MuseumLevelPrice(HierarchyTicketBase):
    """博物馆等级与门票价格关系"""
    class Meta:
        verbose_name = '博物馆等级票价'
        verbose_name_plural = '博物馆等级票价'
        db_table = 'museum_level_price'
        managed = True

class GeoLogicalParkLevelPrice(HierarchyTicketBase):
    """地质公园等级与门票价格关系"""
    class Meta:
        verbose_name = '地质公园等级票价'
        verbose_name_plural = '地质公园等级票价'
        db_table = 'geological_park_level_price'
        managed = True

class ForestParkLevelPrice(HierarchyTicketBase):
    """森林公园等级与门票价格关系"""
    class Meta:
        verbose_name = '森林公园等级票价'
        verbose_name_plural = '森林公园等级票价'
        db_table = 'forest_park_level_price'
        managed = True

class WetlandLevelPrice(HierarchyTicketBase):
    """湿地公园等级与门票价格关系"""
    class Meta:
        verbose_name = '湿地公园等级票价'
        verbose_name_plural = '湿地公园等级票价'
        db_table = 'wetland_level_price'
        managed = True

class CulturalRelicLevelPrice(HierarchyTicketBase):
    """文物保护单位等级与门票价格关系"""
    class Meta:
        verbose_name = '文物保护单位等级票价'
        verbose_name_plural = '文物保护单位等级票价'
        db_table = 'cultural_relic_level_price'
        managed = True

class NatureReserveLevelPrice(HierarchyTicketBase):
    """自然景区等级与门票价格关系"""
    class Meta:
        verbose_name = '自然景区等级票价'
        verbose_name_plural = '自然景区等级票价'
        db_table = 'nature_reserve_level_price'
        managed = True