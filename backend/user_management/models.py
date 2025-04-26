from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    """用户个人资料模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.CharField(max_length=500, blank=True, default='', verbose_name='头像路径')  # 支持任意路径格式
    location = models.CharField(max_length=100, blank=True, default='', verbose_name='所在地')
    last_login = models.DateTimeField(default=timezone.now, verbose_name='最后登录时间')
    
    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

class UserFavorite(models.Model):
    """用户收藏景区模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='用户')
    scenic_id = models.CharField(max_length=20, verbose_name='景区ID')
    added_time = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')
    
    def __str__(self):
        return f"{self.user.username} - 景区ID {self.scenic_id}"
    
    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = '用户收藏'
        unique_together = ['user', 'scenic_id']  # 确保用户不会重复收藏同一景区

class UserActionRecord(models.Model):
    """用户行为记录模型"""
    ACTION_CHOICES = (
        ('login', '登录'),
        ('register', '注册'),
        ('search', '搜索'),
        ('view', '查看'),
        ('favorite', '收藏'),
        ('admin', '管理员操作'),
        ('profile_update', '修改个人信息'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions', verbose_name='用户')
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    details = models.TextField(blank=True, default='', verbose_name='操作详情')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.timestamp}"
    
    class Meta:
        verbose_name = '用户操作记录'
        verbose_name_plural = '用户操作记录'
        ordering = ['-timestamp']  # 按时间倒序排列
