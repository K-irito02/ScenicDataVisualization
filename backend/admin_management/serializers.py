from rest_framework import serializers
from django.contrib.auth.models import User
from user_management.models import UserProfile, UserActionRecord
from .models import SystemErrorLog

class AdminUserSerializer(serializers.ModelSerializer):
    """后台用户列表序列化器"""
    avatar = serializers.CharField(source='profile.avatar', read_only=True)
    location = serializers.CharField(source='profile.location', read_only=True)
    registerTime = serializers.DateTimeField(source='date_joined', read_only=True)
    lastLoginTime = serializers.DateTimeField(source='profile.last_login', read_only=True)
    isAdmin = serializers.BooleanField(source='is_staff', read_only=True)
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'avatar', 'location', 'isAdmin', 'registerTime', 'lastLoginTime', 'status')
        read_only_fields = fields
        
    def get_status(self, obj):
        return "active" if obj.is_active else "disabled"

class AdminUserRecordSerializer(serializers.ModelSerializer):
    """后台用户记录序列化器"""
    userId = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    action = serializers.CharField(source='action_type', read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = UserActionRecord
        fields = ('id', 'userId', 'username', 'action', 'details', 'timestamp')
        read_only_fields = fields

class SystemErrorLogSerializer(serializers.ModelSerializer):
    """系统错误日志序列化器"""
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    error_type_display = serializers.CharField(source='get_error_type_display', read_only=True)
    
    class Meta:
        model = SystemErrorLog
        fields = ['id', 'level', 'level_display', 'error_type', 'error_type_display', 'message', 'traceback', 'path', 
                 'method', 'user_id', 'ip_address', 'timestamp'] 