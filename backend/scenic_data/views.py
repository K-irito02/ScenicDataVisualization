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
        
        # 统计时间段分布
        time_counts = defaultdict(int)
        scenic_map = defaultdict(list)
        
        for item in time_data:
            if item.time_range:
                time_ranges = item.time_range.split(',')
                for time_range in time_ranges:
                    time_range = time_range.strip()
                    if time_range:
                        time_counts[time_range] += 1
                        scenic_map[time_range].append(item.scenic_name)
        
        time_ranges = [
            {'timeRange': time_range, 'count': count}
            for time_range, count in sorted(time_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        result = {
            'time_ranges': time_ranges,
            'scenic_map': scenic_map
        }
        
        return Response(result)

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
            if not item.transport_frequency:
                continue
                
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
            district = request.query_params.get('district', '')  # 添加区县参数
            scenic_type = request.query_params.get('type', '')
            level = request.query_params.get('level', '')
            price_range = request.query_params.get('priceRange', '0,500')
            
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
            
            # 处理价格范围
            min_price = 0
            max_price = 500
            if price_range:
                try:
                    parts = price_range.split(',')
                    if len(parts) == 2:
                        min_price = float(parts[0])
                        max_price = float(parts[1])
                except (ValueError, TypeError, IndexError) as e:
                    print(f"价格范围解析错误: {e}")
            
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
                
            if district:  # 添加区县筛选条件
                query &= Q(district=district)
                
            if scenic_type:
                query &= Q(scenic_type__icontains=scenic_type)
                
            if level:
                query &= Q(scenic_type__icontains=level)
            
            # 执行查询
            try:
                results = ScenicData.objects.filter(query).order_by('name')
                
                # 在Python中处理价格过滤
                filtered_results = []
                for scenic in results:
                    try:
                        price_str = scenic.min_price
                        price = 0
                        if price_str and price_str.strip():
                            try:
                                price = float(price_str)
                            except (ValueError, TypeError):
                                continue
                            
                        if price < min_price or price > max_price:
                            continue
                        filtered_results.append(scenic)
                    except Exception as e:
                        print(f"处理景区价格时出错: {e}")
                        continue
                
                # 如果过滤后没有结果，则返回空列表
                if not filtered_results and min_price > 0:
                    filtered_results = []
                
                # 记录搜索操作(如果用户已登录)
                try:
                    if request.user.is_authenticated:
                        search_details = f'搜索景区: {keyword}'
                        if province or city or district or scenic_type or level:  # 添加区县到记录
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
                    print(f"记录用户操作失败: {e}")
                
                # 按景区属性排序：有景区属性的排在前面
                filtered_results.sort(key=lambda x: 0 if x.scenic_type else 1)
                
                # 应用分页
                total_results = len(filtered_results)
                start_index = (page - 1) * page_size
                end_index = min(start_index + page_size, total_results)
                
                # 获取当前页的结果
                paginated_results = filtered_results[start_index:end_index]
                
                # 序列化返回结果
                serializer = ScenicSearchSerializer(paginated_results, many=True)
                return Response({
                    'results': serializer.data,
                    'total': total_results,
                    'page': page,
                    'page_size': page_size,
                    'pages': (total_results + page_size - 1) // page_size  # 向上取整得到总页数
                })
            except Exception as e:
                print(f"查询或序列化数据时出错: {e}")
                return Response({"error": "数据查询失败"}, status=500)
                
        except Exception as e:
            print(f"搜索视图处理请求时出错: {e}")
            return Response({"error": "服务器内部错误"}, status=500)

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
