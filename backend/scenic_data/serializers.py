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
    
    class Meta:
        model = ScenicData
        fields = ('scenic_id', 'name', 'province', 'city', 'district', 'street',
                 'image_url', 'description', 'min_price', 'level', 'type',
                 'comment_count', 'sentiment_score')
    
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
            for item in obj.scenic_type.split(','):
                if ':' in item:
                    type_name, _ = item.split(':')
                    types.append(type_name.strip())
                elif 'A景区' in item:
                    continue
                else:
                    types.append(item.strip())
            return ', '.join(types) if types else '未分类'
        return '未分类'

class ScenicDetailSerializer(serializers.ModelSerializer):
    """景区详情序列化器"""
    level = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    trafficInfo = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    
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
                # 使用transport_mode字段作为交通方式列表
                modes = []
                if hasattr(obj, 'transport_mode') and obj.transport_mode:
                    modes = obj.transport_mode.split(',')
                    
                for mode in modes:
                    if mode and mode.strip():
                        result.append({
                            'type': mode.strip(),
                            'typeName': self._get_transport_type_name(mode.strip()),
                            'description': obj.transportation
                        })
        except Exception as e:
            print(f"获取交通信息时出错: {e}")
        return result
    
    def _get_transport_type_name(self, type_code):
        """获取交通类型的显示名称"""
        transport_dict = {
            '客车': '长途客车',
            '公交': '公共汽车',
            '火车': '铁路',
            '包车': '包车服务',
            '自驾': '自驾车',
            '摆渡车': '景区摆渡',
            '专车': '专车服务',
            '步行': '步行',
            '地铁': '地铁',
            '飞机': '航空',
            '观光车': '景区观光车',
            '马': '骑马',
            '动车': '高速动车',
            '游艇': '游船/游艇',
            '船': '轮渡/船',
            '索道': '缆车/索道',
            '高铁': '高速铁路',
            '三轮车': '人力三轮'
        }
        return transport_dict.get(type_code, type_code)
    
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