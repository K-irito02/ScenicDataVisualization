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