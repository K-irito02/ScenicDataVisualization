from django.shortcuts import render
from rest_framework import status, viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.db import transaction

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
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 记录注册操作
            UserActionRecord.objects.create(
                user=user,
                action_type='register',
                details='用户注册'
            )
            
            return Response({
                'success': True,
                'message': '注册成功'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': '注册失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

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
