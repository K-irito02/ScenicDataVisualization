from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
import json
import re

class InactiveUserMiddleware(MiddlewareMixin):
    """
    中间件用于检查被禁用的用户，并清除其Token
    """
    
    def process_request(self, request):
        # 获取授权头
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        # 检查是否有Token认证
        if 'Token' in auth_header:
            # 提取token
            token_key = auth_header.split(' ')[1]
            
            # 尝试获取token和用户
            try:
                token = Token.objects.get(key=token_key)
                user = token.user
                
                # 如果用户被禁用，清除token
                if not user.is_active:
                    # 删除token
                    token.delete()
                    
                    # 如果是API请求，返回JSON响应
                    if request.path.startswith('/api/'):
                        response_data = {
                            'detail': '用户已被禁用',
                            'message': '您的账号已被管理员禁用，请联系管理员'
                        }
                        return JsonResponse(response_data, status=403)
            except Token.DoesNotExist:
                pass  # Token不存在，继续正常处理
            except Exception:
                pass  # 其他错误，继续正常处理
        
        return None 

class CustomCorsMiddleware:
    """
    自定义CORS中间件，确保所有响应都包含CORS头信息
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            response = self.__handle_options_request(request)
            return response

        # 处理正常请求
        response = self.get_response(request)
        
        # 为所有响应添加CORS头
        self.__add_cors_headers(response)
        
        return response
    
    def __handle_options_request(self, request):
        """处理OPTIONS预检请求"""
        from django.http import HttpResponse
        
        response = HttpResponse()
        self.__add_cors_headers(response)
        return response
    
    def __add_cors_headers(self, response):
        """添加CORS头信息到响应"""
        # 检查请求的Origin是否已在响应中设置
        if not response.has_header('Access-Control-Allow-Origin'):
            response['Access-Control-Allow-Origin'] = '*'
        
        # 添加其他CORS头
        if not response.has_header('Access-Control-Allow-Methods'):
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        
        if not response.has_header('Access-Control-Allow-Headers'):
            response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, X-Requested-With, X-CSRFToken'
        
        # 允许凭证
        if not response.has_header('Access-Control-Allow-Credentials'):
            response['Access-Control-Allow-Credentials'] = 'true'
        
        # 缓存预检请求结果
        if not response.has_header('Access-Control-Max-Age'):
            response['Access-Control-Max-Age'] = '86400'  # 24小时 