from django.shortcuts import render
from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from user_management.models import UserProfile, UserActionRecord, UserFavorite
from .models import SystemErrorLog
from .serializers import AdminUserSerializer, AdminUserRecordSerializer, SystemErrorLogSerializer
import traceback
import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count

# 创建日志记录器
logger = logging.getLogger(__name__)

# Create your views here.

class IsAdminUser(permissions.BasePermission):
    """
    只允许管理员访问的权限类
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class AdminUserListView(views.APIView):
    """管理员用户列表视图"""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # 获取查询参数
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('pageSize', 10)
            
            # 查询所有用户
            users = User.objects.all().select_related('profile')
            
            # 分页
            paginator = Paginator(users, page_size)
            try:
                users_page = paginator.page(page)
            except PageNotAnInteger:
                users_page = paginator.page(1)
            except EmptyPage:
                users_page = paginator.page(paginator.num_pages)
            
            # 序列化
            serializer = AdminUserSerializer(users_page, many=True)
            
            # 返回结果
            return Response({
                'data': serializer.data,
                'total': paginator.count,
                'page': int(page),
                'pageSize': int(page_size),
                'pages': paginator.num_pages
            })
        except Exception as e:
            # 记录错误
            log_system_error('ERROR', f"获取用户列表失败: {str(e)}", request, e)
            return Response({'error': '获取用户列表失败', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, format=None):
        """切换用户状态（启用/禁用）"""
        try:
            user_id = request.data.get('user_id')
            if not user_id:
                return Response({'error': '未提供用户ID'}, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': f'ID为{user_id}的用户不存在'}, status=status.HTTP_404_NOT_FOUND)
                
            # 不允许管理员禁用自己的账户
            if user.id == request.user.id:
                return Response(
                    {'error': '不能修改当前登录的管理员账户状态'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # 切换用户状态
            user.is_active = not user.is_active
            user.save()
            
            # 记录操作
            action = '启用' if user.is_active else '禁用'
            UserActionRecord.objects.create(
                user=request.user,
                action_type='admin',
                details=f'管理员{action}了用户 {user.username} (ID: {user.id})'
            )
            
            # 返回更新后的用户信息
            serializer = AdminUserSerializer(user)
            return Response({
                'success': True,
                'message': f'已{action}用户 {user.username}',
                'user': serializer.data
            })
            
        except Exception as e:
            # 记录错误
            log_system_error('ERROR', f"切换用户状态失败: {str(e)}", request, e)
            return Response({'error': '切换用户状态失败', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, user_id=None, format=None):
        """更新用户信息"""
        try:
            # 从URL获取用户ID
            if not user_id and 'user_id' not in request.data:
                return Response({'error': '未提供用户ID'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = user_id or request.data.get('user_id')
            
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': f'ID为{user_id}的用户不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 获取要更新的字段
            username = request.data.get('username')
            email = request.data.get('email')
            location = request.data.get('location')
            user_status = request.data.get('status')
            
            # 验证数据并更新
            changes = []
            
            if username and username != user.username:
                # 检查用户名是否已存在
                if User.objects.filter(username=username).exclude(id=user.id).exists():
                    return Response({'error': f'用户名 {username} 已被使用'}, status=status.HTTP_400_BAD_REQUEST)
                user.username = username
                changes.append(f'用户名更新为"{username}"')
                
            if email and email != user.email:
                # 检查邮箱是否已存在
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    return Response({'error': f'邮箱 {email} 已被使用'}, status=status.HTTP_400_BAD_REQUEST)
                user.email = email
                changes.append(f'邮箱更新为"{email}"')
                
            if location is not None:
                # 获取或创建用户资料
                profile, created = UserProfile.objects.get_or_create(user=user)
                if location != profile.location:
                    profile.location = location
                    profile.save()
                    changes.append(f'所在地更新为"{location}"')
                    
            if user_status is not None:
                is_active = user_status == 'active'
                if is_active != user.is_active:
                    # 不允许管理员禁用自己的账户
                    if user.id == request.user.id and not is_active:
                        return Response(
                            {'error': '不能禁用当前登录的管理员账户'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    user.is_active = is_active
                    status_str = '启用' if is_active else '禁用'
                    changes.append(f'用户状态更新为"{status_str}"')
            
            # 如果有更改，保存用户信息
            if changes:
                user.save()
                
                # 记录操作
                details = f'管理员更新了用户 {user.username} (ID: {user.id}) 的信息: ' + ', '.join(changes)
                UserActionRecord.objects.create(
                    user=request.user,
                    action_type='admin',
                    details=details
                )
                
                # 返回更新后的用户信息
                serializer = AdminUserSerializer(user)
                return Response({
                    'success': True,
                    'message': '用户信息已更新',
                    'changes': changes,
                    'user': serializer.data
                })
            else:
                return Response({
                    'success': True,
                    'message': '无需更新，用户信息未变更',
                    'user': AdminUserSerializer(user).data
                })
                
        except Exception as e:
            # 记录错误
            log_system_error('ERROR', f"更新用户信息失败: {str(e)}", request, e)
            return Response({'error': '更新用户信息失败', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminUserRecordView(views.APIView):
    """管理员用户记录视图"""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # 获取查询参数
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('pageSize', 10)
            user_id = request.query_params.get('user_id', None)
            record_type = request.query_params.get('record_type', None)
            start_date = request.query_params.get('start_date', None)
            end_date = request.query_params.get('end_date', None)
            export = request.query_params.get('export', 'false').lower() == 'true'
            
            # 查询用户记录
            records = UserActionRecord.objects.all().select_related('user').order_by('-timestamp')
            
            # 按用户筛选
            if user_id:
                records = records.filter(user_id=user_id)
                
            # 按记录类型筛选
            if record_type:
                records = records.filter(action_type=record_type)
                
            # 按日期范围筛选
            if start_date:
                from django.utils.dateparse import parse_date
                start_date = parse_date(start_date)
                if start_date:
                    from django.utils import timezone
                    import datetime
                    start_datetime = datetime.datetime.combine(start_date, datetime.time.min, tzinfo=timezone.get_current_timezone())
                    records = records.filter(timestamp__gte=start_datetime)
                    
            if end_date:
                from django.utils.dateparse import parse_date
                end_date = parse_date(end_date)
                if end_date:
                    from django.utils import timezone
                    import datetime
                    end_datetime = datetime.datetime.combine(end_date, datetime.time.max, tzinfo=timezone.get_current_timezone())
                    records = records.filter(timestamp__lte=end_datetime)
            
            # 导出数据
            if export:
                return self.export_records(records)
            
            # 生成统计数据
            all_records_queryset = records  # 保存过滤后但未分页的查询集用于统计
            total_records = all_records_queryset.count()
            search_records = all_records_queryset.filter(action_type='search').count()
            favorite_records = all_records_queryset.filter(action_type='favorite').count()
            login_records = all_records_queryset.filter(action_type='login').count()
            register_records = all_records_queryset.filter(action_type='register').count()
            admin_records = all_records_queryset.filter(action_type='admin').count()
            profile_update_records = all_records_queryset.filter(action_type='profile_update').count()
            
            # 获取时间趋势数据
            time_trend_data = self.get_time_trend_data(all_records_queryset)
            
            # 分页
            paginator = Paginator(records, page_size)
            try:
                records_page = paginator.page(page)
            except PageNotAnInteger:
                records_page = paginator.page(1)
            except EmptyPage:
                records_page = paginator.page(paginator.num_pages)
            
            # 序列化
            serializer = AdminUserRecordSerializer(records_page, many=True)
            
            # 构造返回的summary数据
            summary = {
                'totalRecords': total_records,
                'searchRecords': search_records,
                'favoriteRecords': favorite_records,
                'loginRecords': login_records,
                'registerRecords': register_records,
                'adminRecords': admin_records,
                'profileUpdateRecords': profile_update_records,
                'timeTrend': time_trend_data
            }
            
            # 返回结果
            return Response({
                'data': serializer.data,
                'total': paginator.count,
                'page': int(page),
                'pageSize': int(page_size),
                'pages': paginator.num_pages,
                'summary': summary
            })
        except Exception as e:
            # 记录错误
            log_system_error('ERROR', f"获取用户记录失败: {str(e)}", request, e)
            return Response({'error': '获取用户记录失败', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, record_id=None):
        """删除用户记录"""
        try:
            # 检查是否提供了记录ID
            if not record_id:
                record_id = request.query_params.get('id')
                if not record_id:
                    return Response({'error': '未指定记录ID'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 尝试查找记录
            try:
                record = UserActionRecord.objects.get(id=record_id)
            except UserActionRecord.DoesNotExist:
                return Response({'error': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 删除记录
            record.delete()
            
            return Response({'success': True, 'message': '记录已删除'})
        except Exception as e:
            # 记录错误
            log_system_error('ERROR', f"删除用户记录失败: {str(e)}", request, e)
            return Response({'error': '删除用户记录失败', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def export_records(self, queryset):
        """导出用户记录为CSV格式"""
        try:
            import csv
            from django.http import HttpResponse
            from io import StringIO
            
            # 创建CSV响应
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="user_records.csv"'
            
            # 创建CSV写入器
            writer = csv.writer(response)
            
            # 写入表头
            writer.writerow(['记录ID', '用户ID', '用户名', '操作类型', '详情', '时间'])
            
            # 写入数据
            for record in queryset:
                writer.writerow([
                    record.id,
                    record.user.id,
                    record.user.username,
                    record.get_action_type_display(),
                    record.details,
                    record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            return response
        except Exception as e:
            # 记录错误
            logger.error(f"导出用户记录失败: {str(e)}")
            return Response({'error': '导出用户记录失败', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def get_time_trend_data(self, queryset):
        """获取时间趋势数据"""
        try:
            from django.db.models import Count
            from django.db.models.functions import TruncDate
            import datetime
            from django.utils import timezone
            import logging
            
            logger = logging.getLogger(__name__)
            
            # 调试信息
            logger.info(f"开始处理时间趋势数据，当前查询集记录数：{queryset.count()}")
            
            # 获取过去30天的日期范围
            end_date = timezone.now().date()
            start_date = end_date - datetime.timedelta(days=29)
            
            logger.info(f"时间范围：{start_date} 至 {end_date}")
            
            # 如果查询集为空，直接返回空数据
            if queryset.count() == 0:
                logger.warning("查询集为空，返回空时间趋势数据")
                # 生成日期序列用于空数据
                date_range = []
                current_date = start_date
                while current_date <= end_date:
                    date_range.append(current_date)
                    current_date += datetime.timedelta(days=1)
                
                # 返回格式化后的空数据
                return {
                    'xAxisData': [date.strftime('%Y-%m-%d') for date in date_range],
                    'searchData': [0] * len(date_range),
                    'favoriteData': [0] * len(date_range),
                    'loginData': [0] * len(date_range),
                    'registerData': [0] * len(date_range),
                    'adminData': [0] * len(date_range),
                    'profileUpdateData': [0] * len(date_range)
                }
            
            # 按日期分组统计
            try:
                date_counts = queryset.filter(
                    timestamp__date__gte=start_date,
                    timestamp__date__lte=end_date
                ).annotate(
                    date=TruncDate('timestamp')
                ).values('date', 'action_type').annotate(
                    count=Count('id')
                ).order_by('date')
                
                logger.info(f"聚合后的日期统计数量：{len(date_counts)}")
            except Exception as agg_error:
                logger.error(f"日期聚合失败: {str(agg_error)}")
                raise
            
            # 生成日期序列
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date)
                current_date += datetime.timedelta(days=1)
            
            logger.info(f"生成的日期序列长度：{len(date_range)}")
            
            # 初始化数据结构
            search_data = {date: 0 for date in date_range}
            favorite_data = {date: 0 for date in date_range}
            login_data = {date: 0 for date in date_range}
            register_data = {date: 0 for date in date_range}
            admin_data = {date: 0 for date in date_range}
            profile_update_data = {date: 0 for date in date_range}
            
            # 填充数据
            for item in date_counts:
                try:
                    date = item['date'].date() if hasattr(item['date'], 'date') else item['date']
                    if date in date_range:
                        action_type = item['action_type']
                        count_value = int(item['count']) if item['count'] is not None else 0
                        
                        if action_type == 'search':
                            search_data[date] = count_value
                        elif action_type == 'favorite':
                            favorite_data[date] = count_value
                        elif action_type == 'login':
                            login_data[date] = count_value
                        elif action_type == 'register':
                            register_data[date] = count_value
                        elif action_type == 'admin':
                            admin_data[date] = count_value
                        elif action_type == 'profile_update':
                            profile_update_data[date] = count_value
                except Exception as item_error:
                    logger.error(f"处理数据项失败: {str(item_error)}, 项: {item}")
                    continue  # 单项错误不影响整体处理
            
            # 格式化为前端需要的格式
            x_axis_data = [date.strftime('%Y-%m-%d') for date in date_range]
            search_values = [search_data[date] for date in date_range]
            favorite_values = [favorite_data[date] for date in date_range]
            login_values = [login_data[date] for date in date_range]
            register_values = [register_data[date] for date in date_range]
            admin_values = [admin_data[date] for date in date_range]
            profile_update_values = [profile_update_data[date] for date in date_range]
            
            result = {
                'xAxisData': x_axis_data,
                'searchData': search_values,
                'favoriteData': favorite_values,
                'loginData': login_values,
                'registerData': register_values,
                'adminData': admin_values,
                'profileUpdateData': profile_update_values
            }
            
            # 验证返回的数据
            for key, value in result.items():
                if not isinstance(value, list):
                    logger.error(f"返回的{key}不是列表类型: {type(value)}")
                    result[key] = []
                if key != 'xAxisData' and len(value) != len(x_axis_data):
                    logger.error(f"返回的{key}长度({len(value)})与x轴长度({len(x_axis_data)})不匹配")
                    # 确保长度一致
                    result[key] = [0] * len(x_axis_data)
            
            logger.info(f"成功生成时间趋势数据，x轴数据长度: {len(x_axis_data)}")
            
            return result
            
        except Exception as e:
            # 发生错误时返回空数据
            logger.error(f"生成时间趋势数据失败: {str(e)}")
            logger.exception("详细错误信息:")
            
            # 返回格式化后的空数据
            empty_range = 30  # 30天空数据
            empty_dates = [(timezone.now().date() - datetime.timedelta(days=i)) for i in range(empty_range, -1, -1)]
            empty_x_axis = [date.strftime('%Y-%m-%d') for date in empty_dates]
            empty_values = [0] * len(empty_x_axis)
            
            return {
                'xAxisData': empty_x_axis,
                'searchData': empty_values.copy(),
                'favoriteData': empty_values.copy(),
                'loginData': empty_values.copy(),
                'registerData': empty_values.copy(),
                'adminData': empty_values.copy(),
                'profileUpdateData': empty_values.copy()
            }

class SystemErrorLogView(views.APIView):
    """系统错误日志视图"""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        try:
            # 获取查询参数
            level = request.query_params.get('level', None)
            error_type = request.query_params.get('error_type', None)
            days = request.query_params.get('days', None)
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('pageSize', 10)
            
            # 查询错误日志
            logs = SystemErrorLog.objects.all().order_by('-timestamp')
            
            # 按级别筛选
            if level:
                logs = logs.filter(level=level)

            # 按错误类型筛选
            if error_type:
                logs = logs.filter(error_type=error_type)
            
            # 按时间筛选
            if days:
                from django.utils import timezone
                import datetime
                days_ago = timezone.now() - datetime.timedelta(days=int(days))
                logs = logs.filter(timestamp__gte=days_ago)
            
            # 分页
            paginator = Paginator(logs, page_size)
            try:
                logs_page = paginator.page(page)
            except PageNotAnInteger:
                logs_page = paginator.page(1)
            except EmptyPage:
                logs_page = paginator.page(paginator.num_pages)
            
            # 序列化
            serializer = SystemErrorLogSerializer(logs_page, many=True)
            
            # 返回结果
            return Response({
                'data': serializer.data,
                'total': paginator.count,
                'page': int(page),
                'pageSize': int(page_size),
                'pages': paginator.num_pages
            })
        except Exception as e:
            # 记录错误
            log_system_error('ERROR', f"获取错误日志失败: {str(e)}", request, e)
            return Response({'error': '获取错误日志失败', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FrontendErrorLogView(views.APIView):
    """前端错误日志记录视图"""
    # 允许匿名访问，但添加安全检查
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            # 安全检查：验证请求是否来自预期的来源
            is_anonymous_log = 'X-Anonymous-Error-Log' in request.headers
            
            # 获取前端传递的错误信息
            level = request.data.get('level', 'ERROR')
            message = request.data.get('message', '')
            traceback = request.data.get('traceback', '')
            location = request.data.get('location', '')  # 页面位置
            
            if not message:
                return Response({
                    'success': False,
                    'message': '错误信息不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 添加来源标识
            message_prefix = '[匿名错误]' if is_anonymous_log else ''
            
            # 记录前端错误
            error_log = SystemErrorLog(
                level=level,
                error_type='FRONTEND',
                message=f"{message_prefix}{message}",
                traceback=traceback,
                path=location,
                method=request.method,
                user_id=request.user.id if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            error_log.save()
            
            return Response({
                'success': True,
                'message': '前端错误已记录'
            })
        except Exception as e:
            # 记录记录错误时发生的错误
            log_system_error('ERROR', f"记录前端错误失败: {str(e)}", request, e)
            return Response({
                'success': False,
                'message': '记录前端错误失败',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def log_system_error(level, message, request=None, exception=None, error_type='BACKEND'):
    """
    记录系统错误的工具函数
    
    参数:
    - level: 错误级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - message: 错误信息
    - request: 请求对象
    - exception: 异常对象
    - error_type: 错误类型 (FRONTEND, BACKEND)
    """
    try:
        error_log = SystemErrorLog(
            level=level,
            message=message,
            error_type=error_type
        )
        
        # 如果提供了异常对象，记录堆栈跟踪
        if exception:
            error_log.traceback = ''.join(traceback.format_exception(
                type(exception), exception, exception.__traceback__))
        
        # 如果提供了请求对象，记录请求信息
        if request:
            error_log.path = request.path
            error_log.method = request.method
            
            # 记录用户ID(如果已认证)
            if request.user and request.user.is_authenticated:
                error_log.user_id = request.user.id
            
            # 获取IP地址
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                error_log.ip_address = x_forwarded_for.split(',')[0]
            else:
                error_log.ip_address = request.META.get('REMOTE_ADDR')
        
        error_log.save()
        
        # 同时使用标准日志记录
        if level == 'CRITICAL':
            logger.critical(message)
        elif level == 'ERROR':
            logger.error(message)
        elif level == 'WARNING':
            logger.warning(message)
        elif level == 'INFO':
            logger.info(message)
        else:
            logger.debug(message)
            
        return True
    except Exception as e:
        # 如果在记录错误日志时发生错误，记录到标准日志
        logger.critical(f"无法记录系统错误: {str(e)}")
        return False

class UserStatsView(views.APIView):
    """用户统计信息视图"""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request, user_id):
        try:
            # 确认用户存在
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': f'ID为{user_id}的用户不存在'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 获取收藏数量
            favorites_count = UserFavorite.objects.filter(user=user).count()
            
            # 获取搜索次数
            searches_count = UserActionRecord.objects.filter(
                user=user, 
                action_type='search'
            ).count()
            
            # 返回统计数据
            return Response({
                'favorites': favorites_count,
                'searches': searches_count,
                'user_id': user_id,
                'username': user.username
            })
            
        except Exception as e:
            # 记录错误
            log_system_error('ERROR', f"获取用户统计信息失败: {str(e)}", request, e)
            return Response(
                {'error': '获取用户统计信息失败', 'detail': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
