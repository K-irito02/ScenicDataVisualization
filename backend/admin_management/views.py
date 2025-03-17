from django.shortcuts import render
from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from user_management.models import UserProfile, UserActionRecord
from .serializers import AdminUserSerializer, AdminUserRecordSerializer

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
        users = User.objects.all().select_related('profile')
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data)

class AdminUserRecordView(views.APIView):
    """管理员用户记录视图"""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        records = UserActionRecord.objects.all().select_related('user').order_by('-timestamp')
        serializer = AdminUserRecordSerializer(records, many=True)
        return Response(serializer.data)
