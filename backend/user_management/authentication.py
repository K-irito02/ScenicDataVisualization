from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status

class ActiveUserTokenAuthentication(TokenAuthentication):
    """
    扩展的令牌认证，增加对用户活动状态的检查
    如果用户被禁用，则抛出友好的错误信息
    """
    
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        
        # 检查用户是否被禁用
        if not user.is_active:
            raise AuthenticationFailed(
                detail='用户已被禁用',
                code=status.HTTP_403_FORBIDDEN
            )
            
        return user, token 