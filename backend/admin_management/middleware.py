import sys
import traceback
from django.db import DatabaseError, transaction
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from .views import log_system_error

class ErrorLoggingMiddleware:
    """
    捕获和记录系统错误的中间件
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # 使用事务原子性保证数据库操作捕获
            with transaction.atomic():
                response = self.get_response(request)
            
            # 检查响应状态码，记录错误
            if response.status_code >= 500:
                # 添加用户信息调试
                print(f"[ErrorLoggingMiddleware] 500错误: {request.path}, 用户: {request.user}, ID: {getattr(request.user, 'id', 'None')}")
                log_system_error(
                    level='ERROR',
                    message=f'服务器错误: {response.status_code} - {request.path}',
                    request=request
                )
            elif response.status_code == 403:
                print(f"[ErrorLoggingMiddleware] 403权限错误: {request.path}, 用户: {request.user}, ID: {getattr(request.user, 'id', 'None')}")
                log_system_error(
                    level='WARNING',
                    message=f'权限错误: 403 - {request.path}',
                    request=request
                )
            elif response.status_code == 404:
                print(f"[ErrorLoggingMiddleware] 404未找到错误: {request.path}, 用户: {request.user}, ID: {getattr(request.user, 'id', 'None')}")
                log_system_error(
                    level='INFO',
                    message=f'资源未找到: 404 - {request.path}',
                    request=request
                )
            elif response.status_code >= 400:
                # 添加用户信息调试
                print(f"[ErrorLoggingMiddleware] 400错误: {request.path}, 用户: {request.user}, ID: {getattr(request.user, 'id', 'None')}")
                log_system_error(
                    level='WARNING',
                    message=f'客户端错误: {response.status_code} - {request.path}',
                    request=request
                )
            return response
        except DatabaseError as db_error:
            # 专门处理数据库错误
            print(f"[ErrorLoggingMiddleware] 数据库错误: {str(db_error)}, 用户: {request.user}, ID: {getattr(request.user, 'id', 'None')}")
            log_system_error(
                level='CRITICAL',
                message=f'数据库错误: {str(db_error)}',
                request=request,
                exception=db_error,
                error_type='DATABASE'
            )
            # 重新抛出异常，让Django的标准异常处理机制继续处理
            raise
        except PermissionDenied as perm_error:
            # 处理权限错误
            print(f"[ErrorLoggingMiddleware] 权限错误: {str(perm_error)}, 用户: {request.user}, ID: {getattr(request.user, 'id', 'None')}")
            log_system_error(
                level='WARNING',
                message=f'权限错误: {str(perm_error)}',
                request=request,
                exception=perm_error
            )
            raise
        except ObjectDoesNotExist as obj_error:
            # 处理对象不存在错误
            print(f"[ErrorLoggingMiddleware] 对象不存在: {str(obj_error)}, 用户: {request.user}, ID: {getattr(request.user, 'id', 'None')}")
            log_system_error(
                level='WARNING',
                message=f'对象不存在: {str(obj_error)}',
                request=request,
                exception=obj_error
            )
            raise
        except Exception as e:
            # 记录未捕获的异常
            # 添加用户信息调试
            print(f"[ErrorLoggingMiddleware] 未捕获异常: {str(e)}, 用户: {request.user}, ID: {getattr(request.user, 'id', 'None')}")
            
            # 根据异常类型智能判断错误级别
            error_level = self._determine_error_level(e)
            
            log_system_error(
                level=error_level,
                message=f'未捕获的异常: {str(e)}',
                request=request,
                exception=e
            )
            # 重新抛出异常，让Django的标准异常处理机制继续处理
            raise

    def process_exception(self, request, exception):
        """
        处理视图函数中的异常
        """
        # 添加用户信息调试
        print(f"[ErrorLoggingMiddleware] 视图异常: {str(exception)}, 用户: {request.user}, ID: {getattr(request.user, 'id', 'None')}")
        
        # 根据异常类型智能判断错误级别
        error_level = self._determine_error_level(exception)
        
        # 获取完整的堆栈跟踪
        exc_type, exc_value, exc_traceback = sys.exc_info()
        stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # 使用获取到的完整堆栈进行记录
        log_system_error(
            level=error_level,
            message=f'视图异常: {str(exception)}',
            request=request,
            exception=exception,
            stack_trace=stack_trace  # 传递完整堆栈
        )
        # 返回None表示继续正常的异常处理
        return None
    
    def _determine_error_level(self, exception):
        """根据异常类型智能判断错误级别"""
        # 严重错误
        if isinstance(exception, (DatabaseError, transaction.TransactionManagementError)):
            return 'CRITICAL'
        # 权限类错误
        elif isinstance(exception, (PermissionDenied, ObjectDoesNotExist)):
            return 'WARNING'
        # 默认为ERROR级别
        else:
            return 'ERROR' 