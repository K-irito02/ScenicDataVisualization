from rest_framework import serializers
from .models import (
    ScenicData, PriceData, ProvinceTraffic, TimeData, TrafficData,
    ScenicLevelPrice, MuseumLevelPrice, GeoLogicalParkLevelPrice,
    ForestParkLevelPrice, WetlandLevelPrice, CulturalRelicLevelPrice, 
    NatureReserveLevelPrice
)
import json
import re

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
    frontend_type = serializers.SerializerMethodField()
    scenic_type_original = serializers.CharField(source='scenic_type')
    
    class Meta:
        model = ScenicData
        fields = ('scenic_id', 'name', 'province', 'city', 'district', 'street',
                 'image_url', 'description', 'min_price', 'level', 'type', 'price',
                 'image', 'comment_count', 'sentiment_score', 'scenic_type_original',
                 'frontend_type')
    
    def get_level(self, obj):
        """获取景区等级"""
        try:
            if obj.scenic_type:
                # 记录原始类型字段，帮助调试
                print(f"[序列化] 处理景区级别 (ID={obj.scenic_id}, Name={obj.name}): 原始类型={obj.scenic_type}")
                
                # 从类型字段中提取等级信息
                levels = []
                
                # 分别处理不同格式的类型信息
                for item in obj.scenic_type.split(','):
                    item = item.strip()
                    if not item:
                        continue
                        
                    # 处理A级景区等级
                    if 'A景区' in item or '5A' in item or '4A' in item or '3A' in item or '2A' in item or '1A' in item:
                        levels.append(item.strip())
                        print(f"[序列化] 提取到A级景区级别: {item.strip()}")
                    
                    # 处理省级景区
                    elif '省级景区' in item:
                        levels.append('省级景区')
                        print(f"[序列化] 提取到省级景区级别: 省级景区")
                    
                    # 处理类型:级别格式
                    elif ':' in item:
                        try:
                            level_type, level = item.split(':')
                            level = level.strip()
                            if level:
                                levels.append(level)
                                print(f"[序列化] 从'{item}'提取到级别: {level}")
                        except Exception as e:
                            print(f"[警告] 解析类型:级别格式错误: {item}, 错误: {e}")
                
                # 返回处理结果
                if levels:
                    result = ', '.join(levels)
                    print(f"[序列化] 最终级别结果: {result}")
                    return result
                else:
                    print(f"[序列化] 未找到级别信息")
                    return '无等级'
            return '无等级'
        except Exception as e:
            print(f"[错误] 获取景区级别时出错: {e}, ID={obj.scenic_id}")
            return '无等级'
    
    def get_type(self, obj):
        """获取景区类型"""
        try:
            if obj.scenic_type:
                print(f"[序列化] 处理景区类型 (ID={obj.scenic_id}, Name={obj.name})")
                
                # 从类型字段中提取类型信息
                types = []
                
                # 检查是否包含A级景区标识
                is_a_level_scenic = any(item for item in obj.scenic_type.split(',') 
                                     if '景区' in item and ('A景区' in item or '5A' in item or '4A' in item or 
                                                        '3A' in item or '2A' in item or '1A' in item or
                                                        '省级' in item))
                
                # 如果是A级景区，先添加"景区"类型
                if is_a_level_scenic:
                    types.append('景区')
                    print(f"[序列化] 添加景区类型: 景区 (A级景区)")
                    
                # 处理其他类型
                for item in obj.scenic_type.split(','):
                    item = item.strip()
                    if not item:
                        continue
                        
                    # 跳过A级景区标记，已在上面处理
                    if 'A景区' in item or '5A' in item or '4A' in item or '3A' in item or '2A' in item or '1A' in item or '省级景区' in item:
                        continue
                        
                    if ':' in item:
                        try:
                            type_name, _ = item.split(':')
                            type_name = type_name.strip()
                            if type_name and type_name not in types:
                                types.append(type_name)
                                print(f"[序列化] 从'{item}'提取到类型: {type_name}")
                        except Exception as e:
                            print(f"[警告] 解析类型部分错误: {item}, 错误: {e}")
                    else:
                        # 处理没有冒号的类型，但跳过单独的"景区"（因为A级景区已经处理）
                        if item and item != '景区' and item not in types:
                            types.append(item)
                            print(f"[序列化] 添加其他类型: {item}")
                
                # 如果没有找到任何类型，但原始字符串中包含"景区"，添加"景区"类型
                if not types and '景区' in obj.scenic_type:
                    types.append('景区')
                    print(f"[序列化] 添加默认景区类型 (未找到其他类型)")
                
                # 返回处理结果
                if types:
                    result = ', '.join(types)
                    print(f"[序列化] 最终类型结果: {result}")
                    return result
                else:
                    print(f"[序列化] 未找到类型信息")
                    return '未分类'
            return '未分类'
        except Exception as e:
            print(f"[错误] 获取景区类型时出错: {e}, ID={obj.scenic_id}")
            return '未分类'
    
    def get_price(self, obj):
        """获取价格（数值类型，用于排序）"""
        try:
            if obj.min_price:
                price_text = obj.min_price.strip().lower()
                
                # 处理特殊价格值
                if price_text in ['免费', '0', '0元', '0.0', '0.00', 'free', '无需门票']:
                    print(f"[序列化] 景区价格为'{price_text}'，序列化为0元: ID={obj.scenic_id}")
                    return 0
                
                # 尝试提取数字部分
                try:
                    # 尝试匹配价格中的数字部分
                    number_match = re.search(r'(\d+(\.\d+)?)', price_text)
                    if number_match:
                        price = float(number_match.group(1))
                        print(f"[序列化] 从'{price_text}'提取到价格: {price}元")
                        return price
                    
                    # 尝试直接转换
                    price = float(price_text)
                    return price
                except (ValueError, TypeError) as e:
                    print(f"[序列化警告] 景区价格转换错误: ID={obj.scenic_id}, price={obj.min_price}, 错误: {e}")
                    return 0
            
            print(f"[序列化] 景区价格为空，序列化为0元: ID={obj.scenic_id}")
            return 0
        except Exception as e:
            print(f"[序列化错误] 获取景区价格时出错: {e}, ID={obj.scenic_id}")
            return 0
    
    def get_image(self, obj):
        """获取图片URL"""
        try:
            base_url = "https://example.com/images/"  # 替换为实际的图片基础URL
            
            if obj.image_url and obj.image_url.strip():
                # 如果已有完整URL，直接返回
                if obj.image_url.startswith(('http://', 'https://')):
                    return obj.image_url
                # 否则拼接基础URL
                return base_url + obj.image_url
            
            # 默认图片
            return "/images/default-scenic.jpg"
        except Exception as e:
            print(f"[错误] 获取景区图片时出错: {e}, ID={obj.scenic_id}")
            return "/images/default-scenic.jpg"

    def get_frontend_type(self, obj):
        """获取前端展示用的类型，处理特殊类型映射"""
        try:
            # 获取原始类型
            original_type = self.get_type(obj)
            print(f"[序列化] 前端类型映射: 原始类型={original_type}")
            
            # 将"景区"映射为"A级景区"
            if original_type == '景区':
                print(f"[序列化] 前端类型映射: 将'景区'映射为'A级景区'")
                return 'A级景区'
            
            # 其他类型保持不变
            return original_type
        except Exception as e:
            print(f"[错误] 获取前端类型时出错: {e}, ID={obj.scenic_id}")
            return '未分类'

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
    id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    type = serializers.CharField(required=False)
    timeRange = serializers.CharField()
    weekdays = serializers.CharField(required=False)
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