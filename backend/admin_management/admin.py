from django.contrib import admin
from .models import SystemErrorLog

# 系统错误日志模型
@admin.register(SystemErrorLog)
class SystemErrorLogAdmin(admin.ModelAdmin):
    list_display = ('level', 'message', 'path', 'user_id', 'ip_address', 'timestamp')
    list_filter = ('level', 'timestamp')
    search_fields = ('message', 'path', 'ip_address')
    readonly_fields = ('level', 'message', 'traceback', 'path', 'method', 'user_id', 'ip_address', 'timestamp')
    ordering = ('-timestamp',)
