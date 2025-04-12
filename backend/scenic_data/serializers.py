from rest_framework import serializers
from .models import (
    ScenicData, PriceData, ProvinceTraffic, TimeData, TrafficData,
    ScenicLevelPrice, MuseumLevelPrice, GeoLogicalParkLevelPrice,
    ForestParkLevelPrice, WetlandLevelPrice, CulturalRelicLevelPrice, 
    NatureReserveLevelPrice
)
import json

class ScenicDataSerializer(serializers.ModelSerializer):
    """景区数据序列化器"""
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    
    class Meta:
        model = ScenicData
        fields = '__all__'
    
    def get_longitude(self, obj):
        """获取经度"""
        if obj.coordinates:
            try:
                lon, _ = obj.coordinates.split(',')
                return float(lon)
            except (ValueError, AttributeError):
                return None
        return None
    
    def get_latitude(self, obj):
        """获取纬度"""
        if obj.coordinates:
            try:
                _, lat = obj.coordinates.split(',')
                return float(lat)
            except (ValueError, AttributeError):
                return None
        return None

class ScenicSearchSerializer(serializers.ModelSerializer):
    """景区搜索结果序列化器"""
    level = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    scenic_type_original = serializers.CharField(source='scenic_type')
    
    class Meta:
        model = ScenicData
        fields = ('scenic_id', 'name', 'province', 'city', 'district', 'street',
                 'image_url', 'description', 'min_price', 'level', 'type', 'price',
                 'image', 'comment_count', 'sentiment_score', 'scenic_type_original')
    
    def get_level(self, obj):
        """获取景区等级"""
        if obj.scenic_type:
            # 从类型字段中提取等级信息
            levels = []
            for item in obj.scenic_type.split(','):
                if '景区' in item and 'A' in item:
                    levels.append(item.strip())
                if ':' in item:
                    level_type, level = item.split(':')
                    levels.append(level.strip())
            return ', '.join(levels) if levels else '无等级'
        return '无等级'
    
    def get_type(self, obj):
        """获取景区类型"""
        if obj.scenic_type:
            # 从类型字段中提取类型信息
            types = []
            
            # 检查是否包含A级景区标识
            is_a_level_scenic = any(item for item in obj.scenic_type.split(',') 
                                 if '景区' in item and ('A景区' in item or '5A' in item or '4A' in item or '3A' in item or '2A' in item or '1A' in item))
            
            # 如果是A级景区，先添加"景区"类型
            if is_a_level_scenic:
                types.append('景区')
                
            # 处理其他类型
            for item in obj.scenic_type.split(','):
                item = item.strip()
                # 跳过A级景区标记，已在上面处理
                if 'A景区' in item or '5A' in item or '4A' in item or '3A' in item or '2A' in item or '1A' in item:
                    continue
                    
                if ':' in item:
                    type_name, _ = item.split(':')
                    type_name = type_name.strip()
                    if type_name and type_name not in types:
                        types.append(type_name)
                else:
                    # 处理没有冒号的类型，但跳过单独的"景区"（因为A级景区已经处理）
                    if item and item != '景区' and item not in types:
                        types.append(item)
            
            # 如果没有找到任何类型，但原始字符串中包含"景区"，添加"景区"类型
            if not types and '景区' in obj.scenic_type:
                types.append('景区')
                
            return ', '.join(types) if types else '未分类'
        return '未分类'
    
    def get_price(self, obj):
        """获取价格（数值类型，用于排序）"""
        if obj.min_price:
            try:
                return float(obj.min_price)
            except (ValueError, TypeError):
                return 0
        return 0
    
    def get_image(self, obj):
        """获取图片URL"""
        base_url = "https://example.com/images/"  # 替换为实际的图片基础URL
        
        if obj.image_url and obj.image_url.strip():
            # 如果已有完整URL，直接返回
            if obj.image_url.startswith(('http://', 'https://')):
                return obj.image_url
            # 否则拼接基础URL
            return base_url + obj.image_url
        
        # 默认图片
        return "/images/default-scenic.jpg"

class ScenicDetailSerializer(serializers.ModelSerializer):
    """景区详情序列化器"""
    level = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    trafficInfo = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    traffic_info = serializers.CharField(source='transportation')
    
    class Meta:
        model = ScenicData
        exclude = ('high_frequency_words',)
    
    def get_level(self, obj):
        return ScenicSearchSerializer().get_level(obj)
    
    def get_type(self, obj):
        return ScenicSearchSerializer().get_type(obj)
    
    def get_trafficInfo(self, obj):
        """获取交通信息"""
        result = []
        try:
            # 使用transportation字段作为交通信息
            if hasattr(obj, 'transportation') and obj.transportation:    
                result.append({
                    'description': obj.transportation
                    })
        except Exception as e:
            print(f"获取交通信息时出错: {e}")
        return result
    
    
    def get_comments(self, obj):
        """获取评论内容"""
        if not obj.comments:
            return []
        
        comments_text = obj.comments.split('\n')
        return [{'content': comment} for comment in comments_text if comment.strip()]

class ProvinceDistributionSerializer(serializers.Serializer):
    """省份景区分布序列化器"""
    name = serializers.CharField()
    value = serializers.IntegerField()
    scenics = serializers.ListField(child=serializers.DictField(), required=False)

class LevelDistributionSerializer(serializers.Serializer):
    """等级分布序列化器"""
    name = serializers.CharField()
    value = serializers.IntegerField()

class HierarchyLevelPriceSerializer(serializers.ModelSerializer):
    """等级票价关系序列化器"""
    name = serializers.CharField(source='level')
    
    class Meta:
        model = ScenicLevelPrice  # 基础模型，具体使用时可能会替换
        fields = ('name', 'count', 'average_price', 'min_price', 'max_price', 'median_price')

class TimeRangeSerializer(serializers.Serializer):
    """开放时间段序列化器"""
    timeRange = serializers.CharField()
    count = serializers.IntegerField()

class WordCloudItemSerializer(serializers.Serializer):
    """词云项序列化器"""
    name = serializers.CharField()
    value = serializers.IntegerField()

class TransportationLinkSerializer(serializers.Serializer):
    """交通链接序列化器"""
    source = serializers.CharField()
    target = serializers.CharField()
    value = serializers.IntegerField()

class FilterOptionsSerializer(serializers.Serializer):
    """筛选选项序列化器"""
    provinces = serializers.ListField(child=serializers.CharField())
    cities = serializers.ListField(child=serializers.CharField())
    types = serializers.ListField(child=serializers.CharField())
    levels = serializers.ListField(child=serializers.CharField())
    priceRange = serializers.ListField(child=serializers.IntegerField()) 