from django.shortcuts import render
from rest_framework import views, viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.db.models import Count, Min, Max, Avg, F, Q
from django.db import connections
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from collections import defaultdict, Counter
import json
import re

from .models import (
    ScenicData, PriceData, ProvinceTraffic, TimeData, TrafficData,
    ScenicLevelPrice, MuseumLevelPrice, GeoLogicalParkLevelPrice,
    ForestParkLevelPrice, WetlandLevelPrice, CulturalRelicLevelPrice, 
    NatureReserveLevelPrice
)
from .serializers import (
    ScenicDataSerializer, ScenicSearchSerializer, ScenicDetailSerializer,
    ProvinceDistributionSerializer, LevelDistributionSerializer, 
    HierarchyLevelPriceSerializer, TimeRangeSerializer, WordCloudItemSerializer,
    TransportationLinkSerializer, FilterOptionsSerializer
)
from user_management.models import UserActionRecord

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
        with connections['hierarchy_database'].cursor() as cursor:
            cursor.execute("SELECT level, count FROM scenic_level_price")
            scenic_levels = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['scenic_levels'] = scenic_levels
            
            # 景区等级票价
            cursor.execute("SELECT level, average_price FROM scenic_level_price")
            scenic_level_prices = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['scenic_level_prices'] = scenic_level_prices
        
        # 博物馆等级分布
        with connections['hierarchy_database'].cursor() as cursor:
            cursor.execute("SELECT level, count FROM museum_level_price")
            museum_levels = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['museum_levels'] = museum_levels
            
            # 博物馆等级票价
            cursor.execute("SELECT level, average_price FROM museum_level_price")
            museum_level_prices = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['museum_level_prices'] = museum_level_prices
        
        # 地质公园等级分布
        with connections['hierarchy_database'].cursor() as cursor:
            cursor.execute("SELECT level, count FROM geological_park_level_price")
            geo_levels = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['geo_levels'] = geo_levels
            
            # 地质公园等级票价
            cursor.execute("SELECT level, average_price FROM geological_park_level_price")
            geo_level_prices = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['geo_level_prices'] = geo_level_prices
        
        # 森林公园等级分布
        with connections['hierarchy_database'].cursor() as cursor:
            cursor.execute("SELECT level, count FROM forest_park_level_price")
            forest_levels = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['forest_levels'] = forest_levels
            
            # 森林公园等级票价
            cursor.execute("SELECT level, average_price FROM forest_park_level_price")
            forest_level_prices = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['forest_level_prices'] = forest_level_prices
        
        # 湿地公园等级分布
        with connections['hierarchy_database'].cursor() as cursor:
            cursor.execute("SELECT level, count FROM wetland_level_price")
            wetland_levels = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['wetland_levels'] = wetland_levels
            
            # 湿地公园等级票价
            cursor.execute("SELECT level, average_price FROM wetland_level_price")
            wetland_level_prices = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['wetland_level_prices'] = wetland_level_prices
        
        # 文物保护单位等级分布
        with connections['hierarchy_database'].cursor() as cursor:
            cursor.execute("SELECT level, count FROM cultural_relic_level_price")
            cultural_levels = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['cultural_levels'] = cultural_levels
            
            # 文物保护单位等级票价
            cursor.execute("SELECT level, average_price FROM cultural_relic_level_price")
            cultural_level_prices = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['cultural_level_prices'] = cultural_level_prices
        
        # 自然景区等级分布
        with connections['hierarchy_database'].cursor() as cursor:
            cursor.execute("SELECT level, count FROM nature_reserve_level_price")
            nature_levels = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['nature_levels'] = nature_levels
            
            # 自然景区等级票价
            cursor.execute("SELECT level, average_price FROM nature_reserve_level_price")
            nature_level_prices = [{'name': row[0], 'value': row[1]} for row in cursor.fetchall()]
            result['nature_level_prices'] = nature_level_prices
        
        return Response(result)

class TicketPricesView(views.APIView):
    """门票价格数据视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # 获取门票价格数据
        result = {}
        
        # 各类型景区的票价分布数据
        with connections['hierarchy_database'].cursor() as cursor:
            # 景区等级票价分布
            cursor.execute("SELECT level, min_price, max_price, average_price, median_price FROM scenic_level_price")
            result['scenicLevels'] = [
                {
                    'name': row[0], 
                    'min': row[1], 
                    'max': row[2], 
                    'avg': row[3],
                    'median': row[4]
                } for row in cursor.fetchall()
            ]
            
            # 博物馆等级票价分布
            cursor.execute("SELECT level, min_price, max_price, average_price, median_price FROM museum_level_price")
            result['museumLevels'] = [
                {
                    'name': row[0], 
                    'min': row[1], 
                    'max': row[2], 
                    'avg': row[3],
                    'median': row[4]
                } for row in cursor.fetchall()
            ]
            
            # 地质公园等级票价分布
            cursor.execute("SELECT level, min_price, max_price, average_price, median_price FROM geological_park_level_price")
            result['geoLevels'] = [
                {
                    'name': row[0], 
                    'min': row[1], 
                    'max': row[2], 
                    'avg': row[3],
                    'median': row[4]
                } for row in cursor.fetchall()
            ]
            
            # 森林公园等级票价分布
            cursor.execute("SELECT level, min_price, max_price, average_price, median_price FROM forest_park_level_price")
            result['forestLevels'] = [
                {
                    'name': row[0], 
                    'min': row[1], 
                    'max': row[2], 
                    'avg': row[3],
                    'median': row[4]
                } for row in cursor.fetchall()
            ]
            
            # 湿地公园等级票价分布
            cursor.execute("SELECT level, min_price, max_price, average_price, median_price FROM wetland_level_price")
            result['wetlandLevels'] = [
                {
                    'name': row[0], 
                    'min': row[1], 
                    'max': row[2], 
                    'avg': row[3],
                    'median': row[4]
                } for row in cursor.fetchall()
            ]
            
            # 文物保护单位等级票价分布
            cursor.execute("SELECT level, min_price, max_price, average_price, median_price FROM cultural_relic_level_price")
            result['culturalLevels'] = [
                {
                    'name': row[0], 
                    'min': row[1], 
                    'max': row[2], 
                    'avg': row[3],
                    'median': row[4]
                } for row in cursor.fetchall()
            ]
            
            # 自然景区等级票价分布
            cursor.execute("SELECT level, min_price, max_price, average_price, median_price FROM nature_reserve_level_price")
            result['natureLevels'] = [
                {
                    'name': row[0], 
                    'min': row[1], 
                    'max': row[2], 
                    'avg': row[3],
                    'median': row[4]
                } for row in cursor.fetchall()
            ]
        
        return Response(result)

class OpenTimesView(views.APIView):
    """开放时间数据视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # 获取开放时间数据
        time_data = TimeData.objects.all()
        
        # 创建用于存储处理后的数据
        processed_data = []
        
        # 使用字典记录每个景区的ID或名称，避免重复
        scenic_ids = {}
        
        # 第一步：收集所有景区的基本信息
        for item in time_data:
            scenic_id = item.scenic_id or f"scenic_{item.id}"
            if scenic_id not in scenic_ids:
                scenic_ids[scenic_id] = {
                    'id': scenic_id,
                    'name': item.scenic_name,
                    'city': item.city_name,
                    'type': item.type or '其他',  # 默认类型为'其他'
                    'time_ranges': [],
                    'weekdays': item.weekdays or '周一-周日',  # 默认为全周
                }
            
            # 添加时间范围
            if item.time_range:
                time_ranges = item.time_range.split(',')
                for time_range in time_ranges:
                    time_range = time_range.strip()
                    if time_range and time_range not in scenic_ids[scenic_id]['time_ranges']:
                        scenic_ids[scenic_id]['time_ranges'].append(time_range)
        
        # 第二步：整理每个景区的开放时间数据，处理重叠时间段
        for scenic_id, info in scenic_ids.items():
            # 解析并合并时间段
            time_points = set()  # 用集合存储所有小时点，自动去重
            
            for time_range in info['time_ranges']:
                try:
                    # 解析时间范围，例如"08:00-17:30"
                    start_time, end_time = time_range.split('-')
                    
                    # 将时间转换为小时数（简化为整数小时）
                    start_hour = int(start_time.split(':')[0])
                    end_hour = int(end_time.split(':')[0])
                    
                    # 确保结束时间不小于开始时间
                    if end_hour < start_hour:
                        end_hour += 24  # 处理跨天的情况
                    
                    # 添加该时间范围内的所有小时点
                    for hour in range(start_hour, end_hour + 1):
                        hour = hour % 24  # 确保小时在0-23范围内
                        time_points.add(hour)
                        
                except Exception as e:
                    # 如果解析失败，继续处理下一个时间段
                    print(f"解析时间范围失败: {time_range}, 错误: {e}")
                    continue
            
            # 将所有工作日解析为标准格式
            weekdays = self._parse_weekdays(info['weekdays'])
            
            # 将处理后的数据添加到结果列表
            processed_data.append({
                'id': info['id'],
                'name': info['name'],
                'type': info['type'],
                'timeRange': ','.join(info['time_ranges']),
                'weekdays': weekdays,
                'count': 1  # 每个景区只计数一次
            })
        
        # 返回处理后的数据
        result = {
            'time_ranges': processed_data,
            'total_count': len(processed_data)
        }
        
        return Response(result)
    
    def _parse_weekdays(self, weekdays_str):
        """解析工作日字符串为标准格式"""
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
        scenic = get_object_or_404(ScenicData, scenic_id=scenic_id)
        
        # 记录查看操作(如果用户已登录)
        if request.user.is_authenticated:
            UserActionRecord.objects.create(
                user=request.user,
                action_type='view',
                details=f'查看景区词云(ID: {scenic_id})'
            )
        
        word_freq = []
        
        # 只使用真实的高频词数据
        if scenic.high_frequency_words:
            for word_item in scenic.high_frequency_words.split(','):
                if ':' in word_item:
                    try:
                        word, freq = word_item.split(':')
                        word_freq.append({
                            'name': word.strip(),
                            'value': int(freq.strip())
                        })
                    except (ValueError, TypeError):
                        pass
        
        # 不提供示例数据，当没有数据时返回空列表
        return Response(word_freq)

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
            price_range = request.query_params.get('priceRange', '0,500')
            
            # 详细记录请求参数
            print(f"[搜索请求] 关键词: '{keyword}', 省份: '{province}', 城市: '{city}', 区县: '{district}'")
            print(f"[搜索请求] 类型: '{scenic_type}', 级别: '{level}', 价格范围: '{price_range}'")
            
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
            
            # 处理价格范围
            min_price = 0
            max_price = 500
            if price_range:
                try:
                    parts = price_range.split(',')
                    if len(parts) == 2:
                        min_price = float(parts[0])
                        max_price = float(parts[1])
                        print(f"[价格范围] 解析成功: {min_price}-{max_price}")
                except (ValueError, TypeError, IndexError) as e:
                    print(f"[错误] 价格范围解析错误: {e}, 使用默认值: 0-500")
            
            # 构建查询条件
            query = Q()
            
            if keyword:
                query &= (
                    Q(name__icontains=keyword) | 
                    Q(description__icontains=keyword)
                )
                print(f"[查询条件] 添加关键词筛选: '{keyword}'")
            
            if province:
                query &= Q(province=province)
                print(f"[查询条件] 添加省份筛选: '{province}'")
                
            if city:
                query &= Q(city=city)
                print(f"[查询条件] 添加城市筛选: '{city}'")
                
            if district:
                query &= Q(district=district)
                print(f"[查询条件] 添加区县筛选: '{district}'")
            
            # 改进类型和级别的查询方式，对应数据库中实际的数据格式
            if scenic_type or level:
                # 打印调试信息
                print(f"[查询条件] 类型筛选: '{scenic_type}', 级别筛选: '{level}'")
                
                # 处理类型和级别组合
                if scenic_type and level:
                    # 特殊处理A级景区
                    if scenic_type == '景区':
                        print(f"[类型+级别] 特殊处理景区类型: 查询包含'{level}'的景区")
                        query &= Q(scenic_type__icontains=level)
                    else:
                        # 对于其他类型：构建"类型:级别"格式进行精确匹配
                        type_level_pattern = f"{scenic_type}:{level}"
                        print(f"[类型+级别] 执行类型:级别组合搜索: '{type_level_pattern}'")
                        # 尝试两种模式匹配，增加匹配成功率
                        type_query = (
                            Q(scenic_type__icontains=type_level_pattern) |
                            Q(scenic_type__regex=f"{scenic_type}[^:]*:{level}")
                        )
                        query &= type_query
                
                # 仅类型
                elif scenic_type:
                    if scenic_type == '景区':
                        # 景区类型特殊处理：包含所有A级景区
                        print(f"[类型筛选] 执行景区类型搜索: 包含所有A级和省级景区")
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
                        print(f"执行单一类型搜索: {scenic_type}")
                        query &= Q(scenic_type__icontains=scenic_type)
            
            # 执行查询
            try:
                print("[查询执行] 开始执行数据库查询...")
                results = ScenicData.objects.filter(query).order_by('name')
                print(f"[查询结果] 初始查询返回 {results.count()} 条结果")
                
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
                            if price_text in ['免费', '0', '0元', '0.0', '0.00', 'free', '无需门票']:
                                price = 0
                                print(f"[价格处理] 景区价格为'{price_text}'，设置为0元: ID={scenic.scenic_id}, 名称={scenic.name}")
                            else:
                                # 尝试提取数字部分
                                import re
                                # 尝试匹配价格中的数字部分
                                number_match = re.search(r'(\d+(\.\d+)?)', price_text)
                                if number_match:
                                    try:
                                        price = float(number_match.group(1))
                                        print(f"[价格处理] 从'{price_text}'提取到价格: {price}元")
                                    except (ValueError, TypeError) as e:
                                        print(f"[警告] 价格数字部分无法转换: '{number_match.group(1)}', 错误: {e}")
                                        price = 0
                                        print(f"[价格处理] 设置默认价格为0元: ID={scenic.scenic_id}")
                                else:
                                    try:
                                        price = float(price_text)
                                    except (ValueError, TypeError) as e:
                                        print(f"[警告] 景区价格无法解析: ID={scenic.scenic_id}, price={price_str}, 错误: {e}")
                                        # 无法解析的价格视为0元
                                        price = 0
                                        print(f"[价格处理] 无法解析的价格，设置为0元: ID={scenic.scenic_id}")
                        else:
                            print(f"[价格处理] 景区价格为空，设置为0元: ID={scenic.scenic_id}")
                            
                        # 检查价格是否在范围内
                        if price < min_price or price > max_price:
                            print(f"[价格过滤] 景区价格 {price}元 不在范围 {min_price}-{max_price}元 内: ID={scenic.scenic_id}")
                            price_filter_count += 1
                            continue
                            
                        # 价格在范围内，保留此结果
                        print(f"[价格匹配] 景区价格 {price}元 在范围 {min_price}-{max_price}元 内: ID={scenic.scenic_id}, 名称={scenic.name}")
                        filtered_results.append(scenic)
                    except Exception as e:
                        print(f"[错误] 处理景区价格时出错: {e}, ID={scenic.scenic_id}")
                        # 发生异常时，默认保留结果而不是跳过
                        print(f"[价格处理] 异常处理：保留景区 ID={scenic.scenic_id}, 名称={scenic.name}")
                        filtered_results.append(scenic)
                        continue
                
                print(f"[价格过滤] 过滤掉 {price_filter_count} 条结果，剩余 {len(filtered_results)} 条结果")
                
                # 如果过滤后没有结果，则返回空列表
                if not filtered_results:
                    print("[查询结果] 最终过滤后没有匹配的景区")
                    return Response({
                        'results': [],
                        'total': 0,
                        'page': page,
                        'page_size': page_size,
                        'pages': 0
                    })
                
                # 记录搜索操作(如果用户已登录)
                try:
                    if request.user.is_authenticated:
                        search_details = f'搜索景区: {keyword}'
                        if province or city or district or scenic_type or level:
                            filters = []
                            if province: filters.append(f'省份={province}')
                            if city: filters.append(f'城市={city}')
                            if district: filters.append(f'区县={district}')
                            if scenic_type: filters.append(f'类型={scenic_type}')
                            if level: filters.append(f'等级={level}')
                            search_details += f'(筛选: {", ".join(filters)})'
                            
                        UserActionRecord.objects.create(
                            user=request.user,
                            action_type='search',
                            details=search_details
                        )
                except Exception as e:
                    print(f"[警告] 记录用户操作失败: {e}")
                
                # 按景区属性排序：有景区属性的排在前面
                filtered_results.sort(key=lambda x: 0 if x.scenic_type else 1)
                
                # 应用分页
                total_results = len(filtered_results)
                start_index = (page - 1) * page_size
                end_index = min(start_index + page_size, total_results)
                
                # 获取当前页的结果
                paginated_results = filtered_results[start_index:end_index]
                
                # 处理单一结果的情况，确保序列化器正常工作
                if len(paginated_results) == 1:
                    print(f"[单一结果] 查询仅返回1个结果: {paginated_results[0].name}")
                
                # 序列化返回结果
                serializer = ScenicSearchSerializer(paginated_results, many=True)
                serialized_data = serializer.data
                
                # 记录结果数
                print(f"[搜索结果] 总数={total_results}, 当前页={len(paginated_results)}, 页码={page}/{(total_results + page_size - 1) // page_size}")
                
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
            # 记录请求信息以便调试
            print(f"请求省份城市分布数据: {province_name}")
            
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
            
            # 打印结果以便调试
            print(f"找到城市数量: {len(city_counts)}")
            
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
                        action_type='view_province_city_distribution',
                        content=f"查看省份城市分布: {province_name}"
                    )
                except Exception as record_error:
                    print(f"记录用户操作失败: {record_error}")
                    # 忽略记录错误，继续返回数据
                
            print(f"成功返回{province_name}的{len(result)}个城市数据")
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
            # 记录请求信息以便调试
            print(f"请求区县景区分布数据: {province_name}-{city_name}")
            
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
            
            # 打印结果以便调试
            print(f"找到区县数量: {len(district_counts)}")
            
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
                        content=f"查看区县分布: {province_name}-{city_name}"
                    )
                except Exception as record_error:
                    print(f"记录用户操作失败: {record_error}")
                    # 忽略记录错误，继续返回数据
                
            print(f"成功返回{province_name}{city_name}的{len(result)}个区县数据")
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
        
        print(f"[情感分析] 接收到请求参数: 类型={scenic_type}, 级别={level}")
        
        if not scenic_type:
            return Response({"detail": "必须提供景区类型参数"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 初始化查询条件
        query_filter = Q()
        
        # 处理不同景区类型的特殊情况
        if scenic_type == '景区':
            # 景区类型直接按5A、4A等级别查询
            if level:
                # 如果有指定级别，查询该级别的景区
                print(f"[情感分析] 查询指定级别景区: {level}")
                query_filter &= Q(scenic_type__contains=level)
            else:
                # 否则查询所有景区（5A、4A、3A、2A、省级景区）
                print("[情感分析] 查询所有景区等级")
                query_filter &= (
                    Q(scenic_type__contains='5A') | 
                    Q(scenic_type__contains='4A') | 
                    Q(scenic_type__contains='3A') | 
                    Q(scenic_type__contains='2A') | 
                    Q(scenic_type__contains='省级景区')
                )
        elif scenic_type == '水利风景区':
            # 水利风景区查询"是"
            print("[情感分析] 查询水利风景区")
            query_filter &= Q(scenic_type__contains='水利风景区')
            if level == '是':
                # 如果指定为"是"，则查询
                print("[情感分析] 水利风景区级别为'是'")
                pass  # 已经在上面查询了水利风景区，无需额外过滤
        else:
            # 其他类型使用组合查询（例如"森林公园:国家级"）
            print(f"[情感分析] 查询景区类型: {scenic_type}")
            query_filter &= Q(scenic_type__contains=scenic_type)
            if level:
                # 组合查询，找到特定类型特定级别的景区
                print(f"[情感分析] 组合查询: {scenic_type}:{level}")
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
            
            print(f"[情感分析] 查询到景区数量: {scenic_data.count()}")
            
            # 对于景区类型，我们需要提取等级并分组
            result_data = {}
            
            for scenic in scenic_data:
                # 提取景区等级
                level_extracted = self.extract_level(scenic.scenic_type, scenic_type)
                
                if level_extracted:
                    print(f"[情感分析] 景区 '{scenic.name}' 提取到级别: {level_extracted}")
                    print(f"  - 情感得分: {scenic.sentiment_score} (类型: {type(scenic.sentiment_score).__name__})")
                    print(f"  - 情感强度: {scenic.sentiment_magnitude} (类型: {type(scenic.sentiment_magnitude).__name__})")
                    
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
                
                print(f"[情感分析] 级别 '{level_key}' 汇总:")
                print(f"  - 总得分: {data['total_score']}")
                print(f"  - 景区数量: {data['count']}")
                print(f"  - 平均得分: {avg_score}")
                print(f"  - 平均强度: {avg_magnitude}")
                
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
            
            print(f"[情感分析] 最终返回数据数量: {len(response_data)}")
            for idx, item in enumerate(response_data):
                print(f"  数据项 {idx+1}: 级别={item['level']}, 得分={item['avg_sentiment_score']}, 强度={item['avg_sentiment_magnitude']}, 数量={item['count']}")
            
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
                    # 对于没有指定级别的，记为"无级别"
                    return "无级别"
                    
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
        try:
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
                
                # 计算各等级的箱线图数据
                for level, price_data in level_price_map.items():
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
            
            return Response(result)
        except Exception as e:
            logger.error(f"获取景区类型各等级箱线图数据失败: {str(e)}")
            return Response({"error": "获取数据失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)