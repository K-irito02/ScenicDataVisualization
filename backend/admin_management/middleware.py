import sys
from .views import log_system_error

class ErrorLoggingMiddleware:
    """
    捕获和记录系统错误的中间件
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            # 检查响应状态码，记录错误
            if response.status_code >= 500:
                log_system_error(
                    level='ERROR',
                    message=f'服务器错误: {response.status_code} - {request.path}',
                    request=request
                )
            elif response.status_code >= 400:
                log_system_error(
                    level='WARNING',
                    message=f'客户端错误: {response.status_code} - {request.path}',
                    request=request
                )
            return response
        except Exception as e:
            # 记录未捕获的异常
            log_system_error(
                level='CRITICAL',
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
        log_system_error(
            level='ERROR',
            message=f'视图异常: {str(exception)}',
            request=request,
            exception=exception
        )
        # 返回None表示继续正常的异常处理
        return None 