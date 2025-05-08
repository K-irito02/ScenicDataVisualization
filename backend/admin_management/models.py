from django.db import models
from django.utils import timezone
import json

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
        ('DATABASE', '数据库'),
        ('NETWORK', '网络'),
        ('AUTH', '认证'),
        ('PERMISSION', '权限'),
        ('API', 'API错误'),
        ('VALIDATION', '数据验证'),
        ('TIMEOUT', '超时'),
        ('UNKNOWN', '未知类型'),
    )
    
    level = models.CharField(max_length=10, choices=ERROR_LEVELS, default='ERROR', verbose_name='错误级别')
    error_type = models.CharField(max_length=15, choices=ERROR_TYPES, default='BACKEND', verbose_name='错误类型')
    message = models.TextField(verbose_name='错误信息')
    traceback = models.TextField(blank=True, null=True, verbose_name='错误追踪')
    path = models.CharField(max_length=255, blank=True, null=True, verbose_name='请求路径')
    method = models.CharField(max_length=10, blank=True, null=True, verbose_name='请求方法')
    user_id = models.IntegerField(blank=True, null=True, verbose_name='用户ID')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='发生时间')
    context_data = models.TextField(blank=True, null=True, verbose_name='上下文数据')
    
    def save(self, *args, **kwargs):
        """重写save方法，添加调试信息和自动类型判断"""
        print(f"[SystemErrorLog.save] 保存前: user_id={self.user_id}, path={self.path}, 类型={self.error_type}, 级别={self.level}")
        
        # 检查是否硬编码的用户ID
        if self.user_id == 6 and self.path == '/api/statistics/summary':
            import traceback
            print(f"[SystemErrorLog.save] 发现疑似硬编码的用户ID 6，调用栈:")
            print(''.join(traceback.format_stack()))
        
        # 根据错误信息自动判断错误类型，如果尚未设置
        if self.error_type == 'BACKEND' or self.error_type == 'UNKNOWN':
            self.error_type = self._infer_error_type()
        
        # 如果没有堆栈跟踪但有上下文数据，尝试从上下文获取堆栈
        if not self.traceback and self.context_data:
            try:
                context = json.loads(self.context_data)
                if 'stack_trace' in context:
                    self.traceback = context['stack_trace']
            except (json.JSONDecodeError, TypeError):
                pass
        
        # 调用原始save方法
        super().save(*args, **kwargs)
        
        print(f"[SystemErrorLog.save] 保存后: id={self.id}, user_id={self.user_id}, path={self.path}, 类型={self.error_type}")
    
    def _infer_error_type(self):
        """根据错误信息推断错误类型"""
        # 将错误消息和堆栈跟踪文本结合起来用于分析
        analysis_text = f"{self.message} {self.traceback or ''}"
        analysis_text = analysis_text.lower()
        
        if any(term in analysis_text for term in ['database', 'db', 'sql', 'query', 'connection', 'transaction']):
            return 'DATABASE'
        elif any(term in analysis_text for term in ['permission', 'denied', 'access', 'forbidden', '403']):
            return 'PERMISSION'
        elif any(term in analysis_text for term in ['auth', 'login', 'password', 'token', 'jwt', 'unauthorized', '401']):
            return 'AUTH'
        elif any(term in analysis_text for term in ['network', 'connection', 'timeout', 'socket', 'http', 'request failed']):
            return 'NETWORK'
        elif any(term in analysis_text for term in ['api', 'endpoint', 'resource', 'not found', '404', 'route']):
            return 'API'
        elif any(term in analysis_text for term in ['valid', 'invalid', 'schema', 'format', 'required field']):
            return 'VALIDATION'
        elif any(term in analysis_text for term in ['timeout', 'time limit', 'deadline']):
            return 'TIMEOUT'
        elif 'frontend' in analysis_text or 'javascript' in analysis_text or 'browser' in analysis_text:
            return 'FRONTEND'
        
        # 如果无法确定，保持默认
        return 'BACKEND'
    
    def __str__(self):
        return f"{self.get_level_display()} - {self.timestamp}"
    
    class Meta:
        verbose_name = '系统错误日志'
        verbose_name_plural = '系统错误日志'
        ordering = ['-timestamp']  # 按时间倒序排列
