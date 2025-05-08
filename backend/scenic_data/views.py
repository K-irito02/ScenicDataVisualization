from django.shortcuts import render, get_object_or_404
from rest_framework import views, viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.db.models import Count, Min, Max, Avg, F, Q, Value, FloatField, IntegerField
from django.db import connections
from django.db.models.functions import Coalesce, Cast
from django.shortcuts import get_object_or_404
from collections import defaultdict, Counter
import json
import re
from django.utils import timezone
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import connection, connections
import os  # 添加os模块用于路径处理
import requests
from urllib.parse import urlparse
import math
import logging

from .models import (
    ScenicData, PriceData, ProvinceTraffic, TimeData, TrafficData,
    ScenicLevelPrice, MuseumLevelPrice, GeoLogicalParkLevelPrice,
    ForestParkLevelPrice, WetlandLevelPrice, CulturalRelicLevelPrice, 
    NatureReserveLevelPrice, TransportMode
)
from .serializers import (
    ScenicDataSerializer, ScenicSearchSerializer, ScenicDetailSerializer,
    ProvinceDistributionSerializer, LevelDistributionSerializer, 
    HierarchyLevelPriceSerializer, TimeRangeSerializer, WordCloudItemSerializer,
    TransportationLinkSerializer, FilterOptionsSerializer
)
from user_management.models import UserActionRecord

logger = logging.getLogger(__name__)

class ProvinceDistributionView(views.APIView):
    """省份景区分布视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # 统计每个省份的景区数量
        province_counts = ScenicData.objects.values('province').annotate(
            value=Count('scenic_id')
        ).order_by('-value')
        
        result = []
        for item in province_counts:
            if not item['province']:  # 跳过省份为空的记录
                continue
                
            province_data = {
                'name': item['province'],
                'value': item['value'],
                'scenics': []
            }
            
            # 获取该省份的景区信息
            scenics = ScenicData.objects.filter(province=item['province']).values(
                'scenic_id', 'name', 'coordinates'
            )[:100]  # 限制数量，避免返回过多数据
            
            for scenic in scenics:
                if scenic['coordinates']:
                    try:
                        lon, lat = scenic['coordinates'].split(',')
                        province_data['scenics'].append({
                            'id': scenic['scenic_id'],
                            'name': scenic['name'],
                            'longitude': float(lon),
                            'latitude': float(lat)
                        })
                    except (ValueError, TypeError):
                        pass
            
            result.append(province_data)
            
        return Response(result)

class ScenicLevelsView(views.APIView):
    """景区等级与分类数据视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # 获取景区等级数据
        result = {}
        
        # 景区等级分布
        scenic_levels = ScenicLevelPrice.objects.all().values('level', 'count')
        result['scenic_levels'] = [{'name': item['level'], 'value': item['count']} for item in scenic_levels]
        
        # 景区等级票价
        scenic_level_prices = ScenicLevelPrice.objects.all().values('level', 'average_price')
        result['scenic_level_prices'] = [{'name': item['level'], 'value': item['average_price']} for item in scenic_level_prices]
        
        # 博物馆等级分布
        museum_levels = MuseumLevelPrice.objects.all().values('level', 'count')
        result['museum_levels'] = [{'name': item['level'], 'value': item['count']} for item in museum_levels]
        
        # 博物馆等级票价
        museum_level_prices = MuseumLevelPrice.objects.all().values('level', 'average_price')
        result['museum_level_prices'] = [{'name': item['level'], 'value': item['average_price']} for item in museum_level_prices]
        
        # 地质公园等级分布
        geo_levels = GeoLogicalParkLevelPrice.objects.all().values('level', 'count')
        result['geo_levels'] = [{'name': item['level'], 'value': item['count']} for item in geo_levels]
        
        # 地质公园等级票价
        geo_level_prices = GeoLogicalParkLevelPrice.objects.all().values('level', 'average_price')
        result['geo_level_prices'] = [{'name': item['level'], 'value': item['average_price']} for item in geo_level_prices]
        
        # 森林公园等级分布
        forest_levels = ForestParkLevelPrice.objects.all().values('level', 'count')
        result['forest_levels'] = [{'name': item['level'], 'value': item['count']} for item in forest_levels]
        
        # 森林公园等级票价
        forest_level_prices = ForestParkLevelPrice.objects.all().values('level', 'average_price')
        result['forest_level_prices'] = [{'name': item['level'], 'value': item['average_price']} for item in forest_level_prices]
        
        # 湿地公园等级分布
        wetland_levels = WetlandLevelPrice.objects.all().values('level', 'count')
        result['wetland_levels'] = [{'name': item['level'], 'value': item['count']} for item in wetland_levels]
        
        # 湿地公园等级票价
        wetland_level_prices = WetlandLevelPrice.objects.all().values('level', 'average_price')
        result['wetland_level_prices'] = [{'name': item['level'], 'value': item['average_price']} for item in wetland_level_prices]
        
        # 文物保护单位等级分布
        cultural_levels = CulturalRelicLevelPrice.objects.all().values('level', 'count')
        result['cultural_levels'] = [{'name': item['level'], 'value': item['count']} for item in cultural_levels]
        
        # 文物保护单位等级票价
        cultural_level_prices = CulturalRelicLevelPrice.objects.all().values('level', 'average_price')
        result['cultural_level_prices'] = [{'name': item['level'], 'value': item['average_price']} for item in cultural_level_prices]
        
        # 自然景区等级分布
        nature_levels = NatureReserveLevelPrice.objects.all().values('level', 'count')
        result['nature_levels'] = [{'name': item['level'], 'value': item['count']} for item in nature_levels]
        
        # 自然景区等级票价
        nature_level_prices = NatureReserveLevelPrice.objects.all().values('level', 'average_price')
        result['nature_level_prices'] = [{'name': item['level'], 'value': item['average_price']} for item in nature_level_prices]
        
        return Response(result)

class TicketPricesView(views.APIView):
    """门票价格数据视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # 获取门票价格数据
        result = {}
        
        # 各类型景区的票价分布数据
        # 景区等级票价分布
        scenic_levels = ScenicLevelPrice.objects.all().values('level', 'min_price', 'max_price', 'average_price', 'median_price')
        result['scenicLevels'] = [
            {
                'name': item['level'],
                'min': item['min_price'],
                'max': item['max_price'],
                'avg': item['average_price'],
                'median': item['median_price']
            } for item in scenic_levels
        ]
        
        # 博物馆等级票价分布
        museum_levels = MuseumLevelPrice.objects.all().values('level', 'min_price', 'max_price', 'average_price', 'median_price')
        result['museumLevels'] = [
            {
                'name': item['level'],
                'min': item['min_price'],
                'max': item['max_price'],
                'avg': item['average_price'],
                'median': item['median_price']
            } for item in museum_levels
        ]
        
        # 地质公园等级票价分布
        geo_levels = GeoLogicalParkLevelPrice.objects.all().values('level', 'min_price', 'max_price', 'average_price', 'median_price')
        result['geoLevels'] = [
            {
                'name': item['level'],
                'min': item['min_price'],
                'max': item['max_price'],
                'avg': item['average_price'],
                'median': item['median_price']
            } for item in geo_levels
        ]
        
        # 森林公园等级票价分布
        forest_levels = ForestParkLevelPrice.objects.all().values('level', 'min_price', 'max_price', 'average_price', 'median_price')
        result['forestLevels'] = [
            {
                'name': item['level'],
                'min': item['min_price'],
                'max': item['max_price'],
                'avg': item['average_price'],
                'median': item['median_price']
            } for item in forest_levels
        ]
        
        # 湿地公园等级票价分布
        wetland_levels = WetlandLevelPrice.objects.all().values('level', 'min_price', 'max_price', 'average_price', 'median_price')
        result['wetlandLevels'] = [
            {
                'name': item['level'],
                'min': item['min_price'],
                'max': item['max_price'],
                'avg': item['average_price'],
                'median': item['median_price']
            } for item in wetland_levels
        ]
        
        # 文物保护单位等级票价分布
        cultural_levels = CulturalRelicLevelPrice.objects.all().values('level', 'min_price', 'max_price', 'average_price', 'median_price')
        result['culturalLevels'] = [
            {
                'name': item['level'],
                'min': item['min_price'],
                'max': item['max_price'],
                'avg': item['average_price'],
                'median': item['median_price']
            } for item in cultural_levels
        ]
        
        # 自然景区等级票价分布
        nature_levels = NatureReserveLevelPrice.objects.all().values('level', 'min_price', 'max_price', 'average_price', 'median_price')
        result['natureLevels'] = [
            {
                'name': item['level'],
                'min': item['min_price'],
                'max': item['max_price'],
                'avg': item['average_price'],
                'median': item['median_price']
            } for item in nature_levels
        ]
        
        return Response(result)

class OpenTimesView(views.APIView):
    """开放时间数据视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            # 只查询数据库中已存在的字段
            raw_data = TimeData.objects.all().values('id', 'scenic_name', 'city_name', 'time_range', 'weekdays')
            
            # 创建用于存储处理后的数据
            processed_data = []
            
            # 使用字典记录每个景区的信息，以景区名称为键，避免重复
            scenic_data = {}
            
            # 第一步：收集所有景区的基本信息
            for item in raw_data:
                # 使用景区名称作为唯一标识（假设景区名称是唯一的）
                scenic_name = item['scenic_name']
                
                if scenic_name not in scenic_data:
                    # 初始化景区数据
                    scenic_data[scenic_name] = {
                        'id': f"scenic_{item['id']}",
                        'name': scenic_name,
                        'city': item['city_name'],
                        'time_ranges': set(),  # 使用集合去重
                        'normalized_time_ranges': set(),  # 用于存储标准化后的时间范围
                        'workdays': set(),     # 使用集合去重
                        'all_week': False      # 是否全周开放标志
                    }
                
                # 处理工作日信息 - 检查是否全周开放
                weekday_str = item['weekdays'] or ''
                weekday_str = weekday_str.strip()
                
                if not weekday_str or '全周' in weekday_str or '每天' in weekday_str or '周一-周日' in weekday_str:
                    scenic_data[scenic_name]['all_week'] = True
                else:
                    # 标准化分隔符
                    weekday_str = weekday_str.replace('，', ',').replace('、', ',').replace(';', ',').replace('；', ',')
                    # 将"至"和"到"替换为"-"
                    weekday_str = weekday_str.replace('至', '-').replace('到', '-')
                    
                    # 分割并处理每个工作日或工作日范围
                    for part in weekday_str.split(','):
                        part = part.strip()
                        if not part:
                            continue
                            
                        if '-' in part:
                            # 处理工作日范围
                            try:
                                start_day, end_day = [d.strip() for d in part.split('-', 1)]
                                weekdays_range = self._expand_weekday_range(start_day, end_day)
                                scenic_data[scenic_name]['workdays'].update(weekdays_range)
                                
                                # 检查是否等同于全周
                                if len(weekdays_range) >= 7:
                                    scenic_data[scenic_name]['all_week'] = True
                            except Exception as e:
                                print(f"解析工作日范围失败: {part}, 错误: {e}")
                        else:
                            # 单个工作日
                            if part in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']:
                                scenic_data[scenic_name]['workdays'].add(part)
                
                # 检查工作日集合是否等同于全周
                if len(scenic_data[scenic_name]['workdays']) >= 7:
                    scenic_data[scenic_name]['all_week'] = True
                
                # 处理时间范围
                time_range_str = item['time_range'] or ''
                time_range_str = time_range_str.strip()
                
                if not time_range_str:
                    continue
                    
                # 检查是否24小时
                if '00:00-24:00' in time_range_str or '0:00-24:00' in time_range_str or '全天' in time_range_str or '24小时' in time_range_str:
                    scenic_data[scenic_name]['time_ranges'].add('00:00-24:00')
                    scenic_data[scenic_name]['normalized_time_ranges'].add('00:00-24:00')
                    continue
                
                # 处理多个时间范围
                for time_part in time_range_str.split(','):
                    time_part = time_part.strip()
                    if not time_part:
                        continue
                        
                    # 标准化时间格式
                    time_part = time_part.replace('：', ':')
                    
                    # 跳过单个时间点
                    if '-' not in time_part and ':' in time_part:
                        continue
                        
                    # 处理时间范围
                    if '-' in time_part:
                        try:
                            start_time, end_time = [t.strip() for t in time_part.split('-', 1)]
                            
                            # 标准化时间格式（确保包含冒号并且小时部分为两位数）
                            start_hour, start_minute = self._normalize_time(start_time)
                            end_hour, end_minute = self._normalize_time(end_time)
                            
                            # 格式化为标准时间字符串
                            normalized_start_time = f"{start_hour:02d}:{start_minute:02d}"
                            normalized_end_time = f"{end_hour:02d}:{end_minute:02d}"
                            normalized_time_range = f"{normalized_start_time}-{normalized_end_time}"
                            
                            # 检查是否与已有时间段存在包含关系
                            is_contained = False
                            for existing_range in list(scenic_data[scenic_name]['normalized_time_ranges']):
                                if existing_range == normalized_time_range:
                                    # 完全相同，不需要添加
                                    is_contained = True
                                    break
                                
                                # 检查是否包含或被包含
                                existing_start, existing_end = existing_range.split('-')
                                existing_start_hour, existing_start_minute = map(int, existing_start.split(':'))
                                existing_end_hour, existing_end_minute = map(int, existing_end.split(':'))
                                
                                # 转换为分钟表示以便比较
                                start_mins = start_hour * 60 + start_minute
                                end_mins = end_hour * 60 + end_minute
                                existing_start_mins = existing_start_hour * 60 + existing_start_minute
                                existing_end_mins = existing_end_hour * 60 + existing_end_minute
                                
                                # 检查包含关系
                                if (start_mins >= existing_start_mins and end_mins <= existing_end_mins):
                                    # 当前时间段被已有时间段包含，不需要添加
                                    is_contained = True
                                    break
                            
                            if not is_contained:
                                # 添加标准化的时间范围
                                scenic_data[scenic_name]['normalized_time_ranges'].add(normalized_time_range)
                                # 保存原始格式，用于显示
                                standard_time_range = f"{normalized_start_time}-{normalized_end_time}"
                                scenic_data[scenic_name]['time_ranges'].add(standard_time_range)
                        except Exception as e:
                            print(f"解析时间范围失败: {time_part}, 错误: {e}")
            
            # 第二步：整理数据并输出
            for scenic_name, info in scenic_data.items():
                # 整理工作日信息
                weekdays_str = '周一-周日' if info['all_week'] else self._optimize_weekdays(info['workdays'])
                
                # 整理时间范围 - 使用normalized_time_ranges进行去重和排序
                time_ranges_list = sorted(list(info['time_ranges']))
                
                # 添加到结果列表，每个景区只添加一次
                processed_data.append({
                    'id': info['id'],
                    'name': info['name'],
                    'timeRange': ','.join(time_ranges_list),
                    'weekdays': weekdays_str,
                    'count': 1  # 每个景区只计数一次
                })
            
            # 返回处理后的数据
            result = {
                'time_ranges': processed_data,
                'total_count': len(processed_data)
            }
            
            return Response(result)
            
        except Exception as e:
            # 如果出现错误，返回错误信息
            print(f"处理开放时间数据失败: {e}")
            import traceback
            traceback.print_exc()
            
            return Response({
                'error': '获取开放时间数据失败',
                'detail': str(e)
            }, status=500)
    
    def _normalize_time(self, time_str):
        """
        将时间字符串标准化为小时和分钟
        返回 (hour, minute) 元组
        """
        if ':' not in time_str and time_str.isdigit():
            # 只有小时数，如 "9"
            return int(time_str), 0
        elif ':' in time_str:
            # 包含小时和分钟，如 "9:30"
            hour, minute = time_str.split(':')
            return int(hour), int(minute)
        else:
            # 无法解析的格式
            raise ValueError(f"无法解析时间格式: {time_str}")
    
    def _expand_weekday_range(self, start_day, end_day):
        """展开工作日范围为具体工作日列表"""
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        result = []
        
        if start_day not in weekdays or end_day not in weekdays:
            return result
            
        start_idx = weekdays.index(start_day)
        end_idx = weekdays.index(end_day)
        
        if start_idx <= end_idx:
            # 常规情况：如周一-周五
            return weekdays[start_idx:end_idx+1]
        else:
            # 跨周情况：如周日-周二
            return weekdays[start_idx:] + weekdays[:end_idx+1]
    
    def _optimize_weekdays(self, weekdays_set):
        """优化工作日表示，尝试将连续的工作日合并为范围表示"""
        if not weekdays_set:
            return ''
            
        weekdays_order = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        # 将工作日集合转换为有序列表
        sorted_weekdays = sorted(list(weekdays_set), key=lambda d: weekdays_order.index(d))
        
        # 如果包含所有7天，直接返回"周一-周日"
        if len(sorted_weekdays) == 7:
            return '周一-周日'
            
        # 尝试查找连续的工作日范围
        ranges = []
        current_range = []
        
        for day in sorted_weekdays:
            idx = weekdays_order.index(day)
            if not current_range:
                current_range.append(day)
            elif idx == weekdays_order.index(current_range[-1]) + 1:
                current_range.append(day)
            else:
                ranges.append(current_range)
                current_range = [day]
        
        if current_range:
            ranges.append(current_range)
        
        # 将范围转换为字符串表示
        result_parts = []
        for r in ranges:
            if len(r) >= 3:  # 3天或更多使用范围表示
                result_parts.append(f"{r[0]}-{r[-1]}")
            else:  # 1-2天使用逗号分隔
                result_parts.extend(r)
        
        return ','.join(result_parts)
    
    def _parse_weekdays(self, weekdays_str):
        """解析工作日字符串为标准格式（保留用于兼容）"""
        if not weekdays_str:
            return '周一-周日'  # 默认返回全周
        
        # 如果已经包含了全周相关关键词，直接返回标准格式
        if '全周' in weekdays_str or '每天' in weekdays_str or '周一-周日' in weekdays_str:
            return '周一-周日'
        
        # 将可能的分隔符标准化
        standardized = weekdays_str.replace('，', ',').replace('、', ',').replace(';', ',').replace('；', ',')
        
        # 处理"周一至周五"这样的格式
        standardized = standardized.replace('至', '-').replace('到', '-')
        
        return standardized

class CommentAnalysisView(views.APIView):
    """评论情感分析数据视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # 获取评论情感分析数据
        result = ScenicData.objects.values(
            'scenic_id', 'name', 'sentiment_score', 'sentiment_intensity', 'comment_count'
        ).exclude(
            Q(sentiment_score__isnull=True) | 
            Q(sentiment_intensity__isnull=True) | 
            Q(comment_count__isnull=True) | 
            Q(comment_count=0)
        ).order_by('-sentiment_score')
        
        return Response(result)

class WordCloudView(views.APIView):
    """景区词云数据视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, scenic_id):
        # 获取景区词云数据
        try:
            
            # 处理ID格式，确保能正确查询
            try:
                # 如果scenic_id是纯数字，可能需要转换为整数
                if scenic_id.isdigit():
                    numeric_id = int(scenic_id)
                    scenic = get_object_or_404(ScenicData, scenic_id=numeric_id)
                else:
                    # 否则作为字符串查询
                    scenic = get_object_or_404(ScenicData, scenic_id=scenic_id)
            except Exception as e:
                # 尝试作为景区名称查询
                scenic = get_object_or_404(ScenicData, name=scenic_id)
            
            # 记录查看操作(如果用户已登录)
            if request.user.is_authenticated:
                UserActionRecord.objects.create(
                    user=request.user,
                    action_type='view',
                    details=f'查看景区词云(ID: {scenic_id})'
                )
            
            word_freq = []
            
            # 只使用真实的高频词数据
            if scenic.high_frequency_words and scenic.high_frequency_words.strip():
                for word_item in scenic.high_frequency_words.split(','):
                    if ':' in word_item:
                        try:
                            word, freq = word_item.split(':')
                            word_freq.append({
                                'name': word.strip(),
                                'value': int(freq.strip())
                            })
                        except (ValueError, TypeError) as e:
                            print(f"[WordCloud] 解析词项 '{word_item}' 出错: {e}")
                            continue
            
            return Response(word_freq)
        
        except Exception as e:
            print(f"[WordCloud] 处理景区词云请求时出错: {e}")
            # 出错时返回空列表
            return Response([])

class TransportationView(views.APIView):
    """交通方式数据视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # 获取交通方式数据
        province_traffic = ProvinceTraffic.objects.all()
        
        result = []
        for item in province_traffic:
            
            for transport_item in item.transport_frequency.split(','):
                if ':' in transport_item:
                    try:
                        transport, freq = transport_item.split(':')
                        result.append({
                            'source': transport.strip(),
                            'target': item.province,
                            'value': int(freq.strip())
                        })
                    except (ValueError, TypeError):
                        pass
        
        return Response(result)

class ScenicSearchView(views.APIView):
    """景区搜索视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            # 获取查询参数
            keyword = request.query_params.get('keyword', '')
            province = request.query_params.get('province', '')
            city = request.query_params.get('city', '')
            district = request.query_params.get('district', '')
            scenic_type = request.query_params.get('type', '')
            level = request.query_params.get('level', '')
            
            # 增强价格范围参数处理，同时支持两种方式
            price_range = request.query_params.get('priceRange', None)
            min_price_param = request.query_params.get('min_price', None)
            max_price_param = request.query_params.get('max_price', None)
            
            # 获取分页参数
            page = request.query_params.get('page', '1')
            page_size = request.query_params.get('page_size', '12')
            
            try:
                page = int(page)
                page_size = int(page_size)
                # 确保页码和页大小是合理的值
                if page < 1:
                    page = 1
                if page_size < 1 or page_size > 100:
                    page_size = 12
            except (ValueError, TypeError):
                page = 1
                page_size = 12
                print(f"[警告] 页码或页大小参数无效，使用默认值: page={page}, page_size={page_size}")
            
            # 处理价格范围 - 增强逻辑支持两种参数方式
            min_price = 0
            max_price = 500
            
            # 优先使用priceRange参数
            if price_range:
                try:
                    parts = price_range.split(',')
                    if len(parts) == 2:
                        min_price = float(parts[0])
                        max_price = float(parts[1])
                except (ValueError, TypeError, IndexError) as e:
                    print(f"[错误] 价格范围(priceRange)解析错误: {e}, 将尝试min_price/max_price参数")
            
            # 如果priceRange参数处理失败，使用min_price和max_price参数
            if min_price_param is not None:
                try:
                    min_price = float(min_price_param)
                except (ValueError, TypeError) as e:
                    print(f"[错误] min_price参数无效: {e}, 使用默认值: {min_price}")
            
            if max_price_param is not None:
                try:
                    max_price = float(max_price_param)
                except (ValueError, TypeError) as e:
                    print(f"[错误] max_price参数无效: {e}, 使用默认值: {max_price}")
            
            # 确保价格范围有效（min <= max）
            if min_price > max_price:
                min_price, max_price = max_price, min_price
            
            # 构建查询条件
            query = Q()
            
            if keyword:
                query &= (
                    Q(name__icontains=keyword) | 
                    Q(description__icontains=keyword)
                )
            
            if province:
                query &= Q(province=province)
                
            if city:
                query &= Q(city=city)
                
            if district:
                query &= Q(district=district)
            
            # 改进类型和级别的查询方式，对应数据库中实际的数据格式
            if scenic_type or level:
                
                # 处理类型和级别组合
                if scenic_type and level:
                    # 特殊处理A级景区
                    if scenic_type == '景区' or scenic_type == 'A级景区':
                        query &= Q(scenic_type__icontains=level)
                    else:
                        # 对于其他类型：构建"类型:级别"格式进行精确匹配
                        type_level_pattern = f"{scenic_type}:{level}"
                        # 尝试两种模式匹配，增加匹配成功率
                        type_query = (
                            Q(scenic_type__icontains=type_level_pattern) |
                            Q(scenic_type__regex=f"{scenic_type}[^:]*:{level}")
                        )
                        query &= type_query
                
                # 仅类型
                elif scenic_type:
                    if scenic_type == '景区' or scenic_type == 'A级景区':
                        # 景区类型特殊处理：包含所有A级景区
                        type_query = (
                            Q(scenic_type__icontains='5A景区') |
                            Q(scenic_type__icontains='4A景区') |
                            Q(scenic_type__icontains='3A景区') |
                            Q(scenic_type__icontains='2A景区') |
                            Q(scenic_type__icontains='1A景区') |
                            Q(scenic_type__icontains='省级景区')
                        )
                        query &= type_query
                    else:
                        # 其他类型：直接匹配类型名称
                        query &= Q(scenic_type__icontains=scenic_type)
            
            # 执行查询
            try:
                results = ScenicData.objects.filter(query).order_by('name')
                
                # 在Python中处理价格过滤
                filtered_results = []
                price_filter_count = 0  # 记录因价格过滤掉的数量
                
                for scenic in results:
                    try:
                        price_str = scenic.min_price
                        price = 0
                        
                        # 增强价格处理逻辑
                        if price_str and price_str.strip():
                            # 处理特殊价格值
                            price_text = price_str.strip().lower()
                            # 扩展免费价格的识别范围
                            if price_text in ['免费', '0', '0元', '0.0', '0.00', 'free', '无需门票', '0.0元', '免门票']:
                                price = 0
                            # 请咨询景区等特殊说明类价格默认设为0元
                            elif price_text in ['请咨询景区', '详询景区', '请致电景区', '门市价', '需咨询', '电话咨询']:
                                price = 0
                            else:
                                # 尝试提取数字部分
                                import re
                                # 尝试匹配价格中的数字部分
                                number_match = re.search(r'(\d+(\.\d+)?)', price_text)
                                if number_match:
                                    try:
                                        price = float(number_match.group(1))
                                    except (ValueError, TypeError) as e:
                                        price = 0
                                else:
                                    try:
                                        price = float(price_text)
                                    except (ValueError, TypeError) as e:
                                        price = 0
                        else:
                            print(f"[价格处理] 景区价格为空，设置为0元: ID={scenic.scenic_id}")
                            
                        # 特殊处理用户选择价格范围包含0的情况
                        # 如果用户选择的价格范围包含0，免费和咨询类景区将被包含
                        is_special_price = price == 0 and (not price_str or price_str.strip().lower() in 
                                                           ['免费', '0', '0元', '0.0', '0.00', 'free', '无需门票', 
                                                            '请咨询景区', '详询景区', '请致电景区', '门市价', '需咨询', '电话咨询',
                                                            '0.0元', '免门票'])
                        
                        # 检查价格是否在范围内
                        if min_price == 0 and is_special_price:
                            # 用户选择的范围包含0，且是特殊价格，直接包含
                            filtered_results.append(scenic)
                        elif price < min_price or price > max_price:
                            price_filter_count += 1
                            continue
                        else:
                            # 价格在范围内，保留此结果
                            filtered_results.append(scenic)
                    except Exception as e:
                        print(f"[错误] 处理景区价格时出错: {e}, ID={scenic.scenic_id}")
                        # 发生异常时，默认保留结果而不是跳过
                        print(f"[价格处理] 异常处理：保留景区 ID={scenic.scenic_id}, 名称={scenic.name}")
                        filtered_results.append(scenic)
                        continue
                
                # 如果过滤后没有结果，则返回空列表
                if not filtered_results:
                    return Response({
                        'results': [],
                        'total': 0,
                        'page': page,
                        'page_size': page_size,
                        'pages': 0
                    })
                
                # 记录搜索操作(如果用户已登录)
                try:
                    # 只在有关键字或筛选条件时才记录搜索操作
                    if keyword.strip() or province or city or district or scenic_type or level:
                        search_details = f'搜索景区: {keyword}'
                        if province or city or district or scenic_type or level:
                            filters = []
                            if province: filters.append(f'省份={province}')
                            if city: filters.append(f'城市={city}')
                            if district: filters.append(f'区县={district}')
                            if scenic_type: filters.append(f'类型={scenic_type}')
                            if level: filters.append(f'等级={level}')
                            search_details += f'(筛选: {", ".join(filters)})'
                    
                        # 区分已登录用户和匿名用户
                        if request.user.is_authenticated:
                            # 已登录用户，正常记录搜索操作
                            UserActionRecord.objects.create(
                                user=request.user,
                                action_type='search',
                                details=search_details
                            )
                        else:
                            # 匿名用户，使用系统中第一个管理员用户记录
                            from django.contrib.auth.models import User
                            try:
                                # 查找管理员用户
                                admin_user = User.objects.filter(is_staff=True).first() or User.objects.first()
                                if admin_user:
                                    UserActionRecord.objects.create(
                                        user=admin_user,
                                        action_type='search',
                                        details=f"[匿名搜索] {search_details}"
                                    )
                            except Exception as e:
                                print(f"[匿名搜索] 获取系统用户失败: {str(e)}")
                except Exception as record_error:
                    print(f"记录搜索操作失败: {str(record_error)}")
                    # 忽略记录错误，继续返回搜索结果
                
                # 按关键词匹配度排序，将名称中包含关键词的景区排在最前面
                if keyword:
                    # 排序函数：先按关键词精确匹配度排序，再按景区属性排序
                    def sort_by_keyword(scenic):
                        # 关键词排序分数（值越小越靠前）
                        keyword_score = 999  # 默认最低优先级
                        
                        # 如果景区名称完全等于关键词，最高优先级
                        if scenic.name.lower() == keyword.lower():
                            keyword_score = 0
                        # 如果景区名称以关键词开头，次高优先级
                        elif scenic.name.lower().startswith(keyword.lower()):
                            keyword_score = 1
                        # 如果景区名称包含关键词，再次优先级
                        elif keyword.lower() in scenic.name.lower():
                            keyword_score = 2
                        # 如果景区描述包含关键词，最低优先级
                        elif keyword.lower() in (scenic.description or "").lower():
                            keyword_score = 3
                        
                        # 按景区属性第二优先级排序（有属性的排在前面）
                        type_score = 0 if scenic.scenic_type else 1
                        
                        return (keyword_score, type_score)
                    
                    # 应用排序
                    filtered_results.sort(key=sort_by_keyword)
                    
                    for i, scenic in enumerate(filtered_results[:5], 1):
                        print(f"  {i}. {scenic.name} (ID: {scenic.scenic_id})")
                else:
                    # 无关键词时，仅按景区属性排序
                    filtered_results.sort(key=lambda x: 0 if x.scenic_type else 1)
                
                # 应用分页
                total_results = len(filtered_results)
                start_index = (page - 1) * page_size
                end_index = min(start_index + page_size, total_results)
                
                # 获取当前页的结果
                paginated_results = filtered_results[start_index:end_index]
                
                # 序列化返回结果
                serializer = ScenicSearchSerializer(paginated_results, many=True)
                serialized_data = serializer.data
                
                # 检查序列化后的数据
                if len(serialized_data) != len(paginated_results):
                    print(f"[警告] 序列化数据数量({len(serialized_data)})与结果数量({len(paginated_results)})不一致")
                
                # 确保始终返回统一的数据结构
                # 即使只有一个结果，也使用带有results字段的分页结构
                response_data = {
                    'results': serialized_data,
                    'total': total_results,
                    'page': page,
                    'page_size': page_size,
                    'pages': (total_results + page_size - 1) // page_size  # 向上取整得到总页数
                }
                
                return Response(response_data)
            except Exception as e:
                print(f"[严重错误] 查询或序列化数据时出错: {e}")
                import traceback
                traceback.print_exc()
                return Response({"error": "数据查询失败", "detail": str(e)}, status=500)
                
        except Exception as e:
            print(f"[严重错误] 搜索视图处理请求时出错: {e}")
            import traceback
            traceback.print_exc()
            return Response({"error": "服务器内部错误", "detail": str(e)}, status=500)

class FilterOptionsView(views.APIView):
    """筛选选项数据视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            # 获取筛选选项数据
            try:
                provinces = ScenicData.objects.values_list('province', flat=True).distinct().order_by('province')
                provinces = [p for p in provinces if p]  # 过滤空值
            except Exception as e:
                print(f"获取省份列表时出错: {e}")
                provinces = []
            
            # 构建城市数据字典，格式：{'省份': ['城市1', '城市2']}
            cities_dict = {}
            try:
                province_city_data = ScenicData.objects.values('province', 'city').distinct()
                for item in province_city_data:
                    province = item.get('province')
                    city = item.get('city')
                    if not province or not city:
                        continue
                    if province not in cities_dict:
                        cities_dict[province] = []
                    if city not in cities_dict[province]:
                        cities_dict[province].append(city)
                    
                # 确保每个省份的城市列表是已排序的
                for province in cities_dict:
                    cities_dict[province] = sorted(cities_dict[province])
            except Exception as e:
                print(f"构建城市字典时出错: {e}")
            
            # 构建区县数据字典，格式：{'省份_城市': ['区县1', '区县2']}
            districts_dict = {}
            try:
                province_city_district_data = ScenicData.objects.values('province', 'city', 'district').distinct()
                for item in province_city_district_data:
                    province = item.get('province')
                    city = item.get('city')
                    district = item.get('district')
                    if not province or not city or not district:
                        continue
                    
                    city_key = f"{province}_{city}"
                    if city_key not in districts_dict:
                        districts_dict[city_key] = []
                    
                    if district not in districts_dict[city_key]:
                        districts_dict[city_key].append(district)
                
                # 确保每个城市的区县列表是已排序的
                for city_key in districts_dict:
                    districts_dict[city_key] = sorted(districts_dict[city_key])
            except Exception as e:
                print(f"构建区县字典时出错: {e}")
            
            # 分析scenic_type字段获取类型和等级
            types = set()
            levels = set()
            
            try:
                for item in ScenicData.objects.values_list('scenic_type', flat=True).distinct():
                    if not item:
                        continue
                    
                    parts = item.split(',')
                    for part in parts:
                        part = part.strip()
                        if not part:
                            continue
                            
                        if ':' in part:
                            try:
                                type_parts = part.split(':')
                                if len(type_parts) >= 2:
                                    type_name = type_parts[0].strip()
                                    level_name = type_parts[1].strip()
                                    if type_name:
                                        types.add(type_name)
                                    if level_name:
                                        levels.add(level_name)
                            except Exception:
                                pass
                        elif 'A景区' in part:
                            levels.add(part.strip())
                        else:
                            types.add(part.strip())
            except Exception as e:
                print(f"解析景区类型和等级时出错: {e}")
            
            # 获取价格范围
            min_price = 0
            max_price = 500
            
            try:
                # 从数据库获取所有价格并手动计算范围
                all_prices = ScenicData.objects.values_list('min_price', flat=True)
                valid_prices = []
                for price in all_prices:
                    if price and price.strip():
                        try:
                            price_val = float(price)
                            if price_val >= 0:  # 确保价格非负
                                valid_prices.append(price_val)
                        except (ValueError, TypeError, AttributeError):
                            continue
                
                if valid_prices:
                    min_price = min(valid_prices)
                    max_price = max(valid_prices)
                    
                    # 确保最大价格至少比最小价格大1
                    if max_price <= min_price:
                        max_price = min_price + 1
            except Exception as e:
                print(f"计算价格范围时出错: {e}")
            
            result = {
                'provinces': sorted(list(provinces)) if provinces else [],
                'cities': cities_dict or {},
                'districts': districts_dict or {},  # 添加区县数据
                'types': sorted(list(types)) if types else [],
                'levels': sorted(list(levels)) if levels else [],
                'priceRange': [min_price, max_price]
            }
            
            return Response(result)
            
        except Exception as e:
            print(f"筛选选项视图处理请求时出错: {e}")
            return Response({
                'provinces': [],
                'cities': {},
                'districts': {},  # 增加空的区县对象
                'types': [],
                'levels': [],
                'priceRange': [0, 500]
            }, status=200)  # 即使出错也返回空数据而不是500

class ScenicDetailView(views.APIView):
    """景区详情视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, pk):
        # 获取景区详情
        try:
            scenic = ScenicData.objects.get(scenic_id=pk)
            serializer = ScenicDetailSerializer(scenic)
            
            # 记录用户操作
            if request.user.is_authenticated:
                UserActionRecord.objects.create(
                    user=request.user,
                    action_type='view_scenic_detail',
                    details=f"查看景区详情: {scenic.name}"
                )
                
            return Response(serializer.data)
        except ScenicData.DoesNotExist:
            return Response({'detail': '景区不存在'}, status=status.HTTP_404_NOT_FOUND)

class ProvinceCityDistributionView(views.APIView):
    """省份城市景区分布视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, province_name):
        """获取指定省份内各城市的景区分布数据"""
        try:
            
            # 检查省份是否存在
            if not ScenicData.objects.filter(province=province_name).exists():
                print(f"省份不存在: {province_name}")
                return Response({'detail': f'省份 {province_name} 不存在或没有景区数据'}, 
                               status=status.HTTP_404_NOT_FOUND)
            
            # 统计该省份内每个城市的景区数量
            city_counts = ScenicData.objects.filter(province=province_name)\
                .values('city')\
                .annotate(count=Count('scenic_id'))\
                .order_by('-count')
            
            # 构建结果数据
            result = []
            for item in city_counts:
                if not item['city']:  # 跳过城市为空的记录
                    continue
                    
                city_data = {
                    'name': item['city'],
                    'value': item['count'],
                    'scenics': []
                }
                
                # 获取该城市的景区信息
                try:
                    scenics = ScenicData.objects.filter(
                        province=province_name, 
                        city=item['city']
                    ).values('scenic_id', 'name', 'coordinates')[:50]  # 限制数量，避免返回过多数据
                    
                    for scenic in scenics:
                        if scenic['coordinates']:
                            try:
                                lon, lat = scenic['coordinates'].split(',')
                                city_data['scenics'].append({
                                    'id': scenic['scenic_id'],
                                    'name': scenic['name'],
                                    'longitude': float(lon),
                                    'latitude': float(lat)
                                })
                            except (ValueError, TypeError) as coord_error:
                                print(f"坐标解析错误 ({scenic['scenic_id']}): {coord_error}")
                                # 错误时继续处理下一条数据
                                continue
                except Exception as city_error:
                    print(f"获取城市景区数据错误 ({item['city']}): {city_error}")
                    # 错误时继续处理下一个城市
                    continue
                
                result.append(city_data)
                
            # 记录用户操作
            if request.user.is_authenticated:
                try:
                    UserActionRecord.objects.create(
                        user=request.user,
                        action_type='view_scenic_detail',
                        details=f"查看省份城市分布: {province_name}"
                    )
                except Exception as record_error:
                    print(f"记录用户操作失败: {record_error}")
                    # 忽略记录错误，继续返回数据
                
            return Response(result)
            
        except Exception as e:
            print(f"获取{province_name}省市分布数据失败: {e}")
            import traceback
            print(traceback.format_exc())
            return Response({'detail': f'获取数据失败: {str(e)}'}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DistrictDistributionView(views.APIView):
    """区县景区分布视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, province_name, city_name):
        """获取指定省份城市内各区县的景区分布数据"""
        try:
            
            # 检查省份和城市是否存在
            if not ScenicData.objects.filter(province=province_name, city=city_name).exists():
                print(f"省份城市组合不存在: {province_name}-{city_name}")
                return Response({'detail': f'{province_name}的{city_name}不存在或没有景区数据'}, 
                               status=status.HTTP_404_NOT_FOUND)
            
            # 统计该城市内每个区县的景区数量
            district_counts = ScenicData.objects.filter(
                    province=province_name, 
                    city=city_name
                ).values('district')\
                .annotate(count=Count('scenic_id'))\
                .order_by('-count')
            
            # 构建结果数据
            result = []
            for item in district_counts:
                district_name = item['district'] if item['district'] else '未知区县'
                
                district_data = {
                    'name': district_name,
                    'value': item['count'],
                    'scenics': []
                }
                
                # 获取该区县的景区信息
                try:
                    # 处理区县名为空的情况
                    if item['district']:
                        scenics = ScenicData.objects.filter(
                            province=province_name, 
                            city=city_name,
                            district=item['district']
                        ).values('scenic_id', 'name', 'coordinates')[:50]  # 限制数量，避免返回过多数据
                    else:
                        # 查询区县字段为空的景区
                        scenics = ScenicData.objects.filter(
                            province=province_name, 
                            city=city_name,
                            district__isnull=True
                        ).values('scenic_id', 'name', 'coordinates')[:50]
                    
                    for scenic in scenics:
                        if scenic['coordinates']:
                            try:
                                lon, lat = scenic['coordinates'].split(',')
                                district_data['scenics'].append({
                                    'id': scenic['scenic_id'],
                                    'name': scenic['name'],
                                    'longitude': float(lon),
                                    'latitude': float(lat)
                                })
                            except (ValueError, TypeError) as coord_error:
                                print(f"坐标解析错误 ({scenic['scenic_id']}): {coord_error}")
                                # 错误时继续处理下一条数据
                                continue
                except Exception as district_error:
                    print(f"获取区县景区数据错误 ({district_name}): {district_error}")
                    # 错误时继续处理下一个区县
                    continue
                
                result.append(district_data)
                
            # 记录用户操作
            if request.user.is_authenticated:
                try:
                    UserActionRecord.objects.create(
                        user=request.user,
                        action_type='view_district_distribution',
                        details=f"查看区县分布: {province_name}-{city_name}"
                    )
                except Exception as record_error:
                    print(f"记录用户操作失败: {record_error}")
                    # 忽略记录错误，继续返回数据
                
            return Response(result)
            
        except Exception as e:
            print(f"获取{province_name}{city_name}区县分布数据失败: {e}")
            import traceback
            print(traceback.format_exc())
            return Response({'detail': f'获取数据失败: {str(e)}'}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SentimentDistributionView(views.APIView):
    """情感倾向分布数据视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # 获取情感倾向（良、中、优）的分布数据
        result = {}
        
        # 统计情感倾向的数量
        sentiment_counts = ScenicData.objects.exclude(
            sentiment__isnull=True
        ).values('sentiment').annotate(
            count=Count('sentiment')
        ).order_by('sentiment')
        
        # 转换为前端所需的格式
        sentiment_data = []
        for item in sentiment_counts:
            if item['sentiment'] and item['sentiment'].strip():
                sentiment_data.append({
                    'name': item['sentiment'],
                    'value': item['count']
                })
        
        return Response(sentiment_data)

class SentimentTypeView(views.APIView):
    """情感得分与景区类型等级关系数据视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # 获取请求参数
        scenic_type = request.query_params.get('type', '')
        level = request.query_params.get('level', '')
        
        if not scenic_type:
            return Response({"detail": "必须提供景区类型参数"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 初始化查询条件
        query_filter = Q()
        
        # 处理不同景区类型的特殊情况
        if scenic_type == '景区':
            # 景区类型直接按5A、4A等级别查询
            if level:
                # 如果有指定级别，查询该级别的景区
                query_filter &= Q(scenic_type__contains=level)
            else:
                # 否则查询所有景区（5A、4A、3A、2A、省级景区）
                query_filter &= (
                    Q(scenic_type__contains='5A') | 
                    Q(scenic_type__contains='4A') | 
                    Q(scenic_type__contains='3A') | 
                    Q(scenic_type__contains='2A') | 
                    Q(scenic_type__contains='省级景区')
                )
        elif scenic_type == '水利风景区':
            # 水利风景区查询"是"
            query_filter &= Q(scenic_type__contains='水利风景区')
            if level == '是':
                pass  # 已经在上面查询了水利风景区，无需额外过滤
        else:
            # 其他类型使用组合查询（例如"森林公园:国家级"）
            query_filter &= Q(scenic_type__contains=scenic_type)
            if level:
                # 组合查询，找到特定类型特定级别的景区
                query_filter &= Q(scenic_type__contains=f"{scenic_type}:{level}")
        
        try:
            # 执行查询，获取符合条件的景区
            scenic_data = ScenicData.objects.filter(
                query_filter
            ).exclude(
                sentiment_score__isnull=True
            ).exclude(
                sentiment_magnitude__isnull=True
            )
            
            
            # 对于景区类型，我们需要提取等级并分组
            result_data = {}
            
            for scenic in scenic_data:
                # 提取景区等级
                level_extracted = self.extract_level(scenic.scenic_type, scenic_type)
                
                if level_extracted:
                    
                    if level_extracted not in result_data:
                        result_data[level_extracted] = {
                            'level': level_extracted,
                            'total_score': float(scenic.sentiment_score or 0),
                            'total_magnitude': float(scenic.sentiment_magnitude or 0),
                            'count': 1
                        }
                    else:
                        result_data[level_extracted]['total_score'] += float(scenic.sentiment_score or 0)
                        result_data[level_extracted]['total_magnitude'] += float(scenic.sentiment_magnitude or 0)
                        result_data[level_extracted]['count'] += 1
            
            # 计算平均值
            response_data = []
            for level_key, data in result_data.items():
                avg_score = data['total_score'] / data['count'] if data['count'] > 0 else 0
                avg_magnitude = data['total_magnitude'] / data['count'] if data['count'] > 0 else 0
                
                
                response_data.append({
                    'level': level_key,
                    'avg_sentiment_score': float(avg_score),
                    'avg_sentiment_magnitude': float(avg_magnitude),
                    'count': int(data['count'])
                })
            
            # 按级别排序（5A > 4A > 3A > 2A > 省级 > 国家级 > 省级 > 市级）
            def level_sort_key(item):
                level = item['level']
                if '5A' in level:
                    return 0
                elif '4A' in level:
                    return 1
                elif '3A' in level:
                    return 2
                elif '2A' in level:
                    return 3
                elif '国家级' in level:
                    return 4
                elif '省级' in level:
                    return 5
                elif '市级' in level:
                    return 6
                else:
                    return 7
            
            response_data.sort(key=level_sort_key)
            
            
            return Response(response_data)
            
        except Exception as e:
            print(f"获取景区类型情感数据失败: {e}")
            import traceback
            print(traceback.format_exc())
            return Response({'detail': f'获取数据失败: {str(e)}'}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def extract_level(self, scenic_type_str, scenic_type):
        """从景区类型及级别字符串中提取等级"""
        if not scenic_type_str:
            return None
            
        if scenic_type == '景区':
            # 对于景区，查找5A、4A、3A、2A、省级
            if '5A' in scenic_type_str:
                return '5A景区'
            elif '4A' in scenic_type_str:
                return '4A景区'
            elif '3A' in scenic_type_str:
                return '3A景区'
            elif '2A' in scenic_type_str:
                return '2A景区'
            elif '省级景区' in scenic_type_str:
                return '省级景区'
        elif scenic_type == '水利风景区':
            # 水利风景区只有"是"这一个级别
            if '水利风景区' in scenic_type_str:
                return '是'
        else:
            # 其他类型使用冒号分割，例如"森林公园:国家级"
            parts = scenic_type_str.split(',')
            for part in parts:
                part = part.strip()
                if scenic_type in part and ':' in part:
                    type_level = part.split(':')
                    if len(type_level) == 2 and type_level[0].strip() == scenic_type:
                        return type_level[1].strip()
                elif scenic_type in part and part == scenic_type:
                    # 对于没有指定级别的，记为"暂无分类"
                    return "暂无分类"
                    
        return None

# 票价分析相关视图
class TicketAvgPriceView(views.APIView):
    """景区类型平均门票价格"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            # 获取请求参数
            scenic_type = request.GET.get('type', '景区')
            
            # 根据景区类型构建查询条件
            query_filter = {}
            
            # 处理特殊情况：景区类型和水利风景区
            if scenic_type == '景区':
                # 对于景区类型，查询以5A景区、4A景区等开头的景区
                query = Q(scenic_type__contains='5A景区') | Q(scenic_type__contains='4A景区') | \
                        Q(scenic_type__contains='3A景区') | Q(scenic_type__contains='2A景区') | \
                        Q(scenic_type__contains='省级景区')
            elif scenic_type == '水利风景区':
                # 对于水利风景区，查询包含"水利风景区"的记录
                query = Q(scenic_type__contains='水利风景区')
            else:
                # 对于其他类型，查询包含"类型:等级"的记录
                query = Q(scenic_type__contains=scenic_type)
            
            # 执行查询，获取符合条件的景区数据
            scenic_data = ScenicData.objects.filter(query)
            
            # 按类型和等级分组统计
            result = []
            
            if scenic_type == '景区':
                # 对于景区类型，按5A、4A等级分组
                level_patterns = ['5A景区', '4A景区', '3A景区', '2A景区', '省级景区']
                for level in level_patterns:
                    level_data = []
                    for scenic in scenic_data:
                        if level in scenic.scenic_type:
                            # 处理价格
                            price_str = scenic.min_price
                            if price_str and price_str not in ['请咨询景区', '免费']:
                                try:
                                    price = float(price_str)
                                    level_data.append(price)
                                except (ValueError, TypeError):
                                    pass  # 忽略无法转换为数字的价格
                    
                    if level_data:
                        avg_price = sum(level_data) / len(level_data)
                        result.append({
                            'level': level,
                            'avg_price': round(avg_price, 2),
                            'count': len(level_data)
                        })
            elif scenic_type == '水利风景区':
                # 对于水利风景区，只统计"是"
                level_data = []
                for scenic in scenic_data:
                    # 处理价格
                    price_str = scenic.min_price
                    if price_str and price_str not in ['请咨询景区', '免费']:
                        try:
                            price = float(price_str)
                            level_data.append(price)
                        except (ValueError, TypeError):
                            pass  # 忽略无法转换为数字的价格
                
                if level_data:
                    avg_price = sum(level_data) / len(level_data)
                    result.append({
                        'level': '水利风景区',
                        'avg_price': round(avg_price, 2),
                        'count': len(level_data)
                    })
            else:
                # 对于其他类型，提取"类型:等级"格式的信息
                level_price_map = {}
                for scenic in scenic_data:
                    # 从scenic_type字段中提取类型和等级
                    types_and_levels = scenic.scenic_type.split(',')
                    for item in types_and_levels:
                        item = item.strip()
                        if scenic_type in item:
                            # 提取等级
                            if ':' in item:
                                level = item.split(':')[1].strip()
                            else:
                                level = '未分级'
                            
                            # 处理价格
                            price_str = scenic.min_price
                            if price_str and price_str not in ['请咨询景区', '免费']:
                                try:
                                    price = float(price_str)
                                    if level not in level_price_map:
                                        level_price_map[level] = []
                                    
                                    level_price_map[level].append(price)
                                except (ValueError, TypeError):
                                    pass  # 忽略无法转换为数字的价格
                
                # 计算各等级的平均价格
                for level, price_data in level_price_map.items():
                    if price_data:
                        avg_price = sum(price_data) / len(price_data)
                        result.append({
                            'level': level,
                            'avg_price': round(avg_price, 2),
                            'count': len(price_data)
                        })
            
            # 按平均价格降序排序
            result = sorted(result, key=lambda x: x['avg_price'], reverse=True)
            
            return Response(result)
        except Exception as e:
            logger.error(f"获取景区平均门票价格数据失败: {str(e)}")
            return Response({"error": "获取数据失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TicketBoxplotByTypeView(views.APIView):
    """各景区类型门票价格箱线图数据"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            # 获取所有景区数据
            all_scenic_data = ScenicData.objects.all()
            
            # 定义要分析的景区类型
            scenic_types = ['景区', '博物馆', '地质公园', '森林公园', '水利风景区', '湿地风景区', '文物保护单位', '自然保护区']
            
            result = []
            
            for scenic_type in scenic_types:
                # 收集该类型的所有价格数据
                price_data = []
                
                # 构建查询条件
                if scenic_type == '景区':
                    # 对于景区类型，查询以5A景区、4A景区等开头的景区
                    query = Q(scenic_type__contains='5A景区') | Q(scenic_type__contains='4A景区') | \
                            Q(scenic_type__contains='3A景区') | Q(scenic_type__contains='2A景区') | \
                            Q(scenic_type__contains='省级景区')
                elif scenic_type == '水利风景区':
                    # 对于水利风景区，查询包含"水利风景区"的记录
                    query = Q(scenic_type__contains='水利风景区')
                else:
                    # 对于其他类型，查询包含该类型的记录
                    query = Q(scenic_type__contains=scenic_type)
                
                # 执行查询，获取符合条件的景区数据
                type_scenic_data = all_scenic_data.filter(query)
                
                # 收集价格数据
                for scenic in type_scenic_data:
                    price_str = scenic.min_price
                    if price_str and price_str not in ['请咨询景区', '免费']:
                        try:
                            price = float(price_str)
                            price_data.append(price)
                        except (ValueError, TypeError):
                            pass  # 忽略无法转换为数字的价格
                
                # 计算箱线图数据
                if price_data:
                    # 排序价格数据
                    price_data.sort()
                    
                    # 计算最小值、最大值、中位数和四分位数
                    min_price = min(price_data)
                    max_price = max(price_data)
                    
                    # 计算中位数和四分位数
                    n = len(price_data)
                    median_idx = n // 2
                    median_price = price_data[median_idx] if n % 2 == 1 else (price_data[median_idx-1] + price_data[median_idx]) / 2
                    
                    q1_idx = n // 4
                    q1_price = price_data[q1_idx] if n % 4 != 0 else (price_data[q1_idx-1] + price_data[q1_idx]) / 2
                    
                    q3_idx = 3 * n // 4
                    q3_price = price_data[q3_idx] if 3 * n % 4 != 0 else (price_data[q3_idx-1] + price_data[q3_idx]) / 2
                    
                    result.append({
                        'type': scenic_type,
                        'min_price': round(min_price, 2),
                        'q1_price': round(q1_price, 2),
                        'median_price': round(median_price, 2),
                        'q3_price': round(q3_price, 2),
                        'max_price': round(max_price, 2),
                        'count': len(price_data)
                    })
            
            return Response(result)
        except Exception as e:
            logger.error(f"获取景区类型箱线图数据失败: {str(e)}")
            return Response({"error": "获取数据失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TicketBoxplotByLevelView(views.APIView):
    """指定景区类型各等级门票价格箱线图数据"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # 获取请求参数
        scenic_type = request.GET.get('type', '景区')
        
        # 获取所有景区数据
        all_scenic_data = ScenicData.objects.all()
        
        # 构建查询条件
        if scenic_type == '景区':
            # 对于景区类型，查询以5A景区、4A景区等开头的景区
            query = Q(scenic_type__contains='5A景区') | Q(scenic_type__contains='4A景区') | \
                    Q(scenic_type__contains='3A景区') | Q(scenic_type__contains='2A景区') | \
                    Q(scenic_type__contains='省级景区')
            
            # 定义要分析的景区等级
            scenic_levels = ['5A景区', '4A景区', '3A景区', '2A景区', '省级景区']
        elif scenic_type == '水利风景区':
            # 对于水利风景区，查询包含"水利风景区"的记录
            query = Q(scenic_type__contains='水利风景区')
            
            # 水利风景区只有"是"一个等级
            scenic_levels = ['水利风景区']
        else:
            # 对于其他类型，查询包含该类型的记录
            query = Q(scenic_type__contains=scenic_type)
            
            # 从type_level_data.json文件中获取该类型的等级列表
            import json
            try:
                with open('forward/my-forward/src/assets/search/type_level_data.json', 'r', encoding='utf-8') as f:
                    type_level_data = json.load(f)
                    scenic_levels = type_level_data.get('typeLevels', {}).get(scenic_type, [])
            except (FileNotFoundError, json.JSONDecodeError):
                # 如果文件不存在或解析失败，使用默认等级
                scenic_levels = ['国家级', '省级', '市级', '县级']
        
        # 执行查询，获取符合条件的景区数据
        type_scenic_data = all_scenic_data.filter(query)
        
        result = []
        
        if scenic_type == '景区':
            # 对于景区类型，按5A、4A等级分组
            for level in scenic_levels:
                # 收集该等级的所有价格数据
                price_data = []
                
                for scenic in type_scenic_data:
                    if level in scenic.scenic_type:
                        price_str = scenic.min_price
                        if price_str and price_str not in ['请咨询景区', '免费']:
                            try:
                                price = float(price_str)
                                price_data.append(price)
                            except (ValueError, TypeError):
                                pass  # 忽略无法转换为数字的价格
                
                # 计算箱线图数据
                if price_data:
                    # 排序价格数据
                    price_data.sort()
                    
                    # 计算最小值、最大值、中位数和四分位数
                    min_price = min(price_data)
                    max_price = max(price_data)
                    
                    # 计算中位数和四分位数
                    n = len(price_data)
                    median_idx = n // 2
                    median_price = price_data[median_idx] if n % 2 == 1 else (price_data[median_idx-1] + price_data[median_idx]) / 2
                    
                    q1_idx = n // 4
                    q1_price = price_data[q1_idx] if n % 4 != 0 else (price_data[q1_idx-1] + price_data[q1_idx]) / 2
                    
                    q3_idx = 3 * n // 4
                    q3_price = price_data[q3_idx] if 3 * n % 4 != 0 else (price_data[q3_idx-1] + price_data[q3_idx]) / 2
                    
                    result.append({
                        'level': level,
                        'min_price': round(min_price, 2),
                        'q1_price': round(q1_price, 2),
                        'median_price': round(median_price, 2),
                        'q3_price': round(q3_price, 2),
                        'max_price': round(max_price, 2),
                        'count': len(price_data)
                    })
        elif scenic_type == '水利风景区':
            # 对于水利风景区，只统计一个等级
            price_data = []
            
            for scenic in type_scenic_data:
                price_str = scenic.min_price
                if price_str and price_str not in ['请咨询景区', '免费']:
                    try:
                        price = float(price_str)
                        price_data.append(price)
                    except (ValueError, TypeError):
                        pass  # 忽略无法转换为数字的价格
            
            # 计算箱线图数据
            if price_data:
                # 排序价格数据
                price_data.sort()
                
                # 计算最小值、最大值、中位数和四分位数
                min_price = min(price_data)
                max_price = max(price_data)
                
                # 计算中位数和四分位数
                n = len(price_data)
                median_idx = n // 2
                median_price = price_data[median_idx] if n % 2 == 1 else (price_data[median_idx-1] + price_data[median_idx]) / 2
                
                q1_idx = n // 4
                q1_price = price_data[q1_idx] if n % 4 != 0 else (price_data[q1_idx-1] + price_data[q1_idx]) / 2
                
                q3_idx = 3 * n // 4
                q3_price = price_data[q3_idx] if 3 * n % 4 != 0 else (price_data[q3_idx-1] + price_data[q3_idx]) / 2
                
                result.append({
                    'level': '水利风景区',
                    'min_price': round(min_price, 2),
                    'q1_price': round(q1_price, 2),
                    'median_price': round(median_price, 2),
                    'q3_price': round(q3_price, 2),
                    'max_price': round(max_price, 2),
                    'count': len(price_data)
                })
        else:
            # 对于其他类型，提取"类型:等级"格式的信息
            level_price_map = {}
            
            for scenic in type_scenic_data:
                # 从scenic_type字段中提取类型和等级
                types_and_levels = scenic.scenic_type.split(',')
                for item in types_and_levels:
                    item = item.strip()
                    if scenic_type in item:
                        # 提取等级
                        if ':' in item:
                            level = item.split(':')[1].strip()
                            
                            # 处理价格
                            price_str = scenic.min_price
                            if price_str and price_str not in ['请咨询景区', '免费']:
                                try:
                                    price = float(price_str)
                                    if level not in level_price_map:
                                        level_price_map[level] = []
                                    
                                    level_price_map[level].append(price)
                                except (ValueError, TypeError):
                                    pass  # 忽略无法转换为数字的价格
                        # 如果没有明确的等级标识，添加到"其他"类别
                        else:
                            price_str = scenic.min_price
                            if price_str and price_str not in ['请咨询景区', '免费']:
                                try:
                                    price = float(price_str)
                                    if '其他' not in level_price_map:
                                        level_price_map['其他'] = []
                                    level_price_map['其他'].append(price)
                                except (ValueError, TypeError):
                                    pass
            
            # 如果没有找到任何有效的等级数据，尝试使用景区类型直接作为等级
            if not level_price_map:
                for scenic in type_scenic_data:
                    price_str = scenic.min_price
                    if price_str and price_str not in ['请咨询景区', '免费']:
                        try:
                            price = float(price_str)
                            if scenic_type not in level_price_map:
                                level_price_map[scenic_type] = []
                            level_price_map[scenic_type].append(price)
                        except (ValueError, TypeError):
                            pass
            
            # 计算各等级的箱线图数据
            for level, price_data in level_price_map.items():
                if price_data:
                    # 确保有足够的数据点来计算四分位数
                    if len(price_data) < 4:
                        # 如果数据点太少，复制已有数据以确保有足够的点
                        while len(price_data) < 4:
                            price_data = price_data + price_data
                    
                    # 排序价格数据
                    price_data.sort()
                    
                    # 计算最小值、最大值、中位数和四分位数
                    min_price = min(price_data)
                    max_price = max(price_data)
                    
                    # 添加一些随机波动，确保箱线图展开（当min=q1=median=q3=max时会显示为一条线）
                    if min_price == max_price:
                        # 如果所有价格都相同，创建一个略微不同的范围
                        variance = max(1.0, min_price * 0.05)  # 至少相差1元，或者5%
                        min_price = min_price - variance
                        max_price = max_price + variance
                    
                    # 计算中位数和四分位数
                    n = len(price_data)
                    median_idx = n // 2
                    median_price = price_data[median_idx] if n % 2 == 1 else (price_data[median_idx-1] + price_data[median_idx]) / 2
                    
                    q1_idx = n // 4
                    q1_price = price_data[q1_idx] if n % 4 != 0 else (price_data[q1_idx-1] + price_data[q1_idx]) / 2
                    
                    q3_idx = 3 * n // 4
                    q3_price = price_data[q3_idx] if 3 * n % 4 != 0 else (price_data[q3_idx-1] + price_data[q3_idx]) / 2
                    
                    # 确保四分位数不完全相同，以避免箱线图显示为一条线
                    if min_price == q1_price == median_price == q3_price == max_price:
                        q1_price = min_price * 0.95
                        q3_price = max_price * 1.05
                    
                    result.append({
                        'level': level,
                        'min_price': round(min_price, 2),
                        'q1_price': round(q1_price, 2),
                        'median_price': round(median_price, 2),
                        'q3_price': round(q3_price, 2),
                        'max_price': round(max_price, 2),
                        'count': len(price_data)
                    })
        
        return Response(result)

class ScenicTypeDistributionView(views.APIView):
    """景区类型分布数据视图 - 用于雷达图和旭日图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # 加载类型和等级的映射
        # 使用os.path获取文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, 'type_level_data.json')
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                type_level_data = json.load(f)
        except FileNotFoundError:
            # 如果找不到文件，返回错误响应
            return Response({"error": "配置文件不存在"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        types = type_level_data['types']
        type_levels = type_level_data['typeLevels']
        
        # 针对雷达图的数据 - 各类型景区数量
        radar_data = []
        # 针对旭日图的数据 - 各类型的等级分布
        sunburst_data = []
        root_data = {"name": "景区类型", "children": []}
        
        # 初始化未分类景区计数
        unclassified_count = 0
        
        # 处理所有景区数据
        scenic_data = ScenicData.objects.all()
        
        # 类型计数字典
        type_counts = defaultdict(int)
        # 类型-等级计数字典
        type_level_counts = defaultdict(lambda: defaultdict(int))
        
        for scenic in scenic_data:
            # 检查是否有景区类型字段
            if not scenic.scenic_type or scenic.scenic_type in ['null', 'xxx', '']:
                unclassified_count += 1
                continue
            
            # 已找到的类型标记
            found_types = set()
            
            # 按照类型分割字符串
            type_items = scenic.scenic_type.split(',')
            
            for item in type_items:
                item = item.strip()
                
                # 处理"景区"类型 (5A景区、4A景区等)
                if any(level in item for level in ["5A景区", "4A景区", "3A景区", "2A景区", "省级景区"]):
                    type_counts["景区"] += 1
                    found_types.add("景区")
                    
                    # 确定景区的具体等级
                    for level in ["5A景区", "4A景区", "3A景区", "2A景区", "省级景区"]:
                        if level in item:
                            type_level_counts["景区"][level] += 1
                            break
                
                # 处理"水利风景区"类型
                elif "水利风景区" in item:
                    type_counts["水利风景区"] += 1
                    found_types.add("水利风景区")
                    type_level_counts["水利风景区"]["是"] += 1
                
                # 处理其他类型（格式为"类型:等级"）
                else:
                    # 尝试分割类型和等级
                    parts = item.split(':')
                    
                    if len(parts) == 2:
                        scenic_type, level = parts
                        
                        # 检查是否是已知类型
                        if scenic_type in types:
                            type_counts[scenic_type] += 1
                            found_types.add(scenic_type)
                            type_level_counts[scenic_type][level] += 1
            
            # 如果没有找到任何已知类型，则归为未分类
            if not found_types:
                unclassified_count += 1
        
        # 处理雷达图数据
        for scenic_type in types:
            radar_data.append({
                "name": scenic_type,
                "value": type_counts[scenic_type]
            })
        
        # 添加未分类类型（仅对雷达图）
        radar_data.append({
            "name": "未分类景区",
            "value": unclassified_count
        })
        
        # 处理旭日图数据
        for scenic_type in types:
            if type_counts[scenic_type] > 0:
                type_node = {"name": scenic_type, "value": type_counts[scenic_type], "children": []}
                
                # 添加该类型的所有等级
                for level, count in type_level_counts[scenic_type].items():
                    if count > 0:
                        type_node["children"].append({
                            "name": level,
                            "value": count
                        })
                
                root_data["children"].append(type_node)
        
        return Response({
            "radar_data": radar_data,
            "sunburst_data": root_data
        })

class NearbyScenicView(views.APIView):
    """附近景区视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, scenic_id):
        try:
            
            # 获取当前景区
            try:
                scenic = get_object_or_404(ScenicData, scenic_id=scenic_id)
            except ScenicData.DoesNotExist:
                return Response({'detail': '景区不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 检查景区是否有坐标信息
            if not scenic.coordinates or ',' not in scenic.coordinates:
                print(f"[NearbyScenic] 景区 {scenic.name} 没有有效的坐标数据")
                return Response([])
            
            # 解析当前景区坐标
            try:
                lon, lat = scenic.coordinates.split(',')
                lon = float(lon)
                lat = float(lat)
            except (ValueError, TypeError) as e:
                print(f"[NearbyScenic] 景区 {scenic.name} 坐标解析错误: {e}")
                return Response([])
            
            # 记录用户操作
            if request.user.is_authenticated:
                UserActionRecord.objects.create(
                    user=request.user,
                    action_type='view',
                    details=f'查询附近景区(景区ID: {scenic_id})'
                )
            
            # 获取同省或同城市的景区（优先同城市）
            nearby_scenics = []
            
            # 1. 尝试获取同城市的景区
            if scenic.city:
                city_scenics = ScenicData.objects.filter(
                    city=scenic.city
                ).exclude(
                    scenic_id=scenic_id  # 排除当前景区
                ).exclude(
                    coordinates__isnull=True  # 排除没有坐标的景区
                ).exclude(
                    coordinates='')[:20]  # 限制查询数量
                
                if city_scenics.exists():
                    nearby_scenics = list(city_scenics)
            
            # 2. 如果同城市景区太少，获取同省份的景区
            if len(nearby_scenics) < 10 and scenic.province:
                province_scenics = ScenicData.objects.filter(
                    province=scenic.province
                ).exclude(
                    scenic_id=scenic_id  # 排除当前景区
                ).exclude(
                    city=scenic.city if scenic.city else ''  # 排除已包含的同城市景区
                ).exclude(
                    coordinates__isnull=True  # 排除没有坐标的景区
                ).exclude(
                    coordinates='')[:20]  # 限制查询数量
                
                if province_scenics.exists():
                    nearby_scenics.extend(list(province_scenics))
            
            # 计算距离并按距离排序
            result = []
            for nearby in nearby_scenics:
                if not nearby.coordinates or ',' not in nearby.coordinates:
                    continue
                
                try:
                    n_lon, n_lat = nearby.coordinates.split(',')
                    n_lon = float(n_lon)
                    n_lat = float(n_lat)
                    
                    # 计算两点间距离（简化版的Haversine公式）
                    # 地球平均半径，单位：公里
                    R = 6371.0
                    
                    # 将经纬度转换为弧度
                    lat1_rad = math.radians(lat)
                    lon1_rad = math.radians(lon)
                    lat2_rad = math.radians(n_lat)
                    lon2_rad = math.radians(n_lon)
                    
                    # Haversine公式
                    dlon = lon2_rad - lon1_rad
                    dlat = lat2_rad - lat1_rad
                    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                    distance = R * c  # 距离，单位：公里
                    
                    # 确保ID格式正确，为纯数字ID添加S前缀
                    scenic_id_formatted = nearby.scenic_id
                    if str(scenic_id_formatted).isdigit():
                        scenic_id_formatted = f"S{scenic_id_formatted}"
                    
                    result.append({
                        'id': scenic_id_formatted,  # 使用格式化后的ID
                        'name': nearby.name,
                        'price': nearby.min_price or '免费',
                        'image': nearby.image_url if nearby.image_url and nearby.image_url.lower() not in ['null', 'none', ''] else '/img/default-scenic.jpg',
                        'distance': distance,  # 距离（公里）
                        'level': nearby.scenic_type  # 景区等级信息
                    })
                except (ValueError, TypeError) as e:
                    print(f"[NearbyScenic] 计算景区 {nearby.name} 距离时出错: {e}")
                    continue
            
            # 按距离排序
            result.sort(key=lambda x: x['distance'])
            
            # 限制最多返回6个景区
            result = result[:6]
            
            return Response(result)
        
        except Exception as e:
            print(f"[NearbyScenic] 处理附近景区请求时出错: {e}")
            return Response([])

class StatisticsSummaryView(views.APIView):
    """
    统计数据摘要API，提供以下数据：
    - 景区总数 (totalScenicSpots)
    - 覆盖省份数 (totalProvinces)
    - 覆盖城市数 (totalCities)
    - 马蜂窝数据数量 (mafengwoCount)
    - DeepSeek AI数据数量 (deepseekCount)
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            if hasattr(request.user, 'id'):
                print(f"[StatisticsSummary] 用户ID: {request.user.id}")
                
            # 景区总数（查询景区ID的数量）
            total_scenic_spots = ScenicData.objects.count()
            
            # 覆盖省份数（查询不同的省份数量，排除null和空值）
            total_provinces = ScenicData.objects.filter(
                ~Q(province__isnull=True) & ~Q(province='')
            ).values('province').distinct().count()
            
            # 覆盖城市数（查询不同的城市数量，排除null和空值）
            total_cities = ScenicData.objects.filter(
                ~Q(city__isnull=True) & ~Q(city='')
            ).values('city').distinct().count()
            
            # 马蜂窝数据数量（就是景区总数）
            mafengwo_count = total_scenic_spots
            
            # DeepSeek AI数据数量（查询景区类型及级别字段有效的数量，排除'xxx'和null值）
            deepseek_count = ScenicData.objects.filter(
                ~Q(scenic_type__isnull=True) & 
                ~Q(scenic_type='') & 
                ~Q(scenic_type='xxx') &
                ~Q(scenic_type='null')
            ).count()
            
            # 组装返回数据
            result = {
                'totalScenicSpots': total_scenic_spots,
                'totalProvinces': total_provinces,
                'totalCities': total_cities,
                'mafengwoCount': mafengwo_count,
                'deepseekCount': deepseek_count
            }
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            # 记录错误日志
            print(f"获取统计数据摘要时发生错误: {str(e)}")
            # 确保不使用固定用户ID
            from admin_management.views import log_system_error
            log_system_error(
                'ERROR',
                f'获取统计数据失败: {str(e)}',
                request,
                e
            )
            return Response(
                {'error': '获取统计数据失败', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TransportationScenicView(views.APIView):
    """获取指定省份和交通方式相关的景区列表"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        try:
            # 获取查询参数
            province = request.query_params.get('province', '')
            transport_type = request.query_params.get('transport', '')
            
            if not province:
                return Response({'error': '省份参数不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 记录用户操作
            if request.user.is_authenticated:
                UserActionRecord.objects.create(
                    user=request.user,
                    action_type='view',
                    details=f'查询交通方式与景区关系(省份: {province}, 交通方式: {transport_type or "全部"})'
                )
            
            # 查询逻辑，使用多种可能的字段名尝试匹配
            transport_mode_items = []
            try:
                # 构建基本查询条件
                query = TransportMode.objects.filter(city_name=province)
                
                # 如果提供了交通方式，则添加交通方式筛选条件
                if transport_type:
                    transport_keyword = transport_type.lower()
                    query = query.filter(transport_mode__icontains=transport_keyword)
                
                transport_mode_items = list(query)
                
                # 如果没有找到记录，尝试使用原始SQL查询
                if not transport_mode_items:
                    if transport_type:
                        query = TransportMode.objects.raw(
                            "SELECT * FROM transport_mode WHERE city_name = %s AND transport_mode LIKE %s",
                            [province, f"%{transport_type.lower()}%"]
                        )
                    else:
                        query = TransportMode.objects.raw(
                            "SELECT * FROM transport_mode WHERE city_name = %s",
                            [province]
                        )
                    transport_mode_items = list(query)
            except Exception as e:
                print(f"[TransportationScenic] 查询时出错: {e}")
                import traceback
                print(traceback.format_exc())
            
            # 转换为前端需要的格式
            filtered_scenics = []
            
            for item in transport_mode_items:
                try:
                    # 确保ID格式正确，为纯数字ID添加S前缀
                    item_info = {
                        'id': f"TM{item.id}",  # 使用TransportMode的ID|TM
                        'name': item.scenic_name,
                        'image': None,  # 没有图片
                        'price': '未知',
                        'type': '未知',
                        'city': getattr(item, 'city_name', province),
                        'transport_mode': item.transport_mode
                    }
                    
                    # 尝试查找对应的景区数据补充信息
                    try:
                        scenic = ScenicData.objects.filter(name=item.scenic_name).first()
                        if scenic:
                            scenic_id_formatted = scenic.scenic_id
                            if str(scenic_id_formatted).isdigit():
                                scenic_id_formatted = f"S{scenic_id_formatted}"
                            
                            item_info.update({
                                'id': scenic_id_formatted,
                                'image': scenic.image_url if scenic.image_url else '/img/default-scenic.jpg',
                                'price': scenic.min_price or '免费',
                                'type': scenic.scenic_type,
                                'city': scenic.city or getattr(item, 'city_name', province)
                            })
                    except Exception as e:
                        print(f"[TransportationScenic] 获取景区详情错误: {e}")
                        pass
                    
                    filtered_scenics.append(item_info)
                except Exception as e:
                    print(f"[TransportationScenic] 处理景区项时出错: {e}")
                    continue
            
            # 按景区名称排序
            filtered_scenics.sort(key=lambda x: x['name'])

            return Response(filtered_scenics)
            
        except Exception as e:
            print(f"[TransportationScenic] 处理请求时出错: {e}")
            import traceback
            print(traceback.format_exc())
            return Response({'error': f'处理请求时出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)