from django.shortcuts import render
from rest_framework import status, viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
import random
from .utils import redis_client  # 从utils导入redis_client

from .models import UserProfile, UserFavorite, UserActionRecord
from django.contrib.auth.models import User
from .serializers import (
    LoginSerializer, RegisterSerializer, UserProfileSerializer,
    ProfileUpdateSerializer, UserFavoriteSerializer
)

class LoginView(APIView):
    """用户登录视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # 更新最后登录时间
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.last_login = timezone.now()
            profile.save()
            
            # 记录登录操作
            UserActionRecord.objects.create(
                user=user,
                action_type='login',
                details='用户登录'
            )
            
            # 获取或创建令牌
            token, created = Token.objects.get_or_create(user=user)
            
            # 准备响应数据
            response_data = {
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'avatar': profile.avatar,
                'location': profile.location,
                'is_admin': user.is_staff
            }
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    """用户注册视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        print(f"收到注册请求，数据: {request.data}")
        serializer = RegisterSerializer(data=request.data)
        
        try:
            if serializer.is_valid():
                print("数据验证通过，开始创建用户")
                user = serializer.save()
                print(f"用户创建成功: {user.username}")
                
                # 记录注册操作
                UserActionRecord.objects.create(
                    user=user,
                    action_type='register',
                    details='用户注册'
                )
                print("注册操作记录已创建")
                
                return Response({
                    'success': True,
                    'message': '注册成功'
                }, status=status.HTTP_201_CREATED)
            else:
                print(f"数据验证失败，错误信息: {serializer.errors}")
                return Response({
                    'success': False,
                    'message': '注册失败',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"注册过程发生异常: {str(e)}")
            return Response({
                'success': False,
                'message': f'注册失败: {str(e)}',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileUpdateView(APIView):
    """用户资料更新视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # 记录更新操作
            UserActionRecord.objects.create(
                user=request.user,
                action_type='update_profile',
                details='更新个人资料'
            )
            
            # 准备响应数据
            user = request.user
            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'avatar': profile.avatar,
                    'location': profile.location,
                    'isAdmin': user.is_staff
                }
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class FavoriteToggleView(APIView):
    """景区收藏切换视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        scenic_id = request.data.get('scenic_id')
        if not scenic_id:
            return Response({
                'success': False,
                'message': '缺少景区ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            favorite, created = UserFavorite.objects.get_or_create(
                user=request.user,
                scenic_id=scenic_id
            )
            
            if not created:
                # 如果已存在，则取消收藏
                favorite.delete()
                is_favorite = False
                action_details = f'取消收藏景区(ID: {scenic_id})'
            else:
                is_favorite = True
                action_details = f'收藏景区(ID: {scenic_id})'
            
            # 记录收藏操作
            UserActionRecord.objects.create(
                user=request.user,
                action_type='favorite',
                details=action_details
            )
            
            return Response({
                'success': True,
                'is_favorite': is_favorite
            })

class UserFavoritesView(generics.ListAPIView):
    """用户收藏列表视图"""
    serializer_class = UserFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user)

class SendEmailCodeView(APIView):
    """发送邮箱验证码视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'success': False,
                'message': '请提供邮箱地址'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成6位随机验证码
        code = ''.join(random.choices('0123456789', k=6))
        
        try:
            # 发送邮件
            send_mail(
                subject='景区数据分析系统 - 验证码',
                message=f'您的验证码是：{code}，有效期为5分钟。请勿将验证码泄露给他人。',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            
            # 将验证码保存到Redis，设置5分钟过期
            redis_key = f'email_code:{email}'
            redis_client.setex(redis_key, 300, code)
            
            return Response({
                'success': True,
                'message': '验证码已发送，请查收邮件'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': '验证码发送失败，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
