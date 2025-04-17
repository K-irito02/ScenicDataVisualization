from django.db import models
from django.utils import timezone

# Create your models here.

class SystemErrorLog(models.Model):
    """系统错误日志模型"""
    ERROR_LEVELS = (
        ('DEBUG', '调试'),
        ('INFO', '信息'),
        ('WARNING', '警告'),
        ('ERROR', '错误'),
        ('CRITICAL', '严重'),
    )
    
    ERROR_TYPES = (
        ('FRONTEND', '前端'),
        ('BACKEND', '后端'),
    )
    
    level = models.CharField(max_length=10, choices=ERROR_LEVELS, default='ERROR', verbose_name='错误级别')
    error_type = models.CharField(max_length=10, choices=ERROR_TYPES, default='BACKEND', verbose_name='错误类型')
    message = models.TextField(verbose_name='错误信息')
    traceback = models.TextField(blank=True, null=True, verbose_name='错误追踪')
    path = models.CharField(max_length=255, blank=True, null=True, verbose_name='请求路径')
    method = models.CharField(max_length=10, blank=True, null=True, verbose_name='请求方法')
    user_id = models.IntegerField(blank=True, null=True, verbose_name='用户ID')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='发生时间')
    
    def __str__(self):
        return f"{self.get_level_display()} - {self.timestamp}"
    
    class Meta:
        verbose_name = '系统错误日志'
        verbose_name_plural = '系统错误日志'
        ordering = ['-timestamp']  # 按时间倒序排列
