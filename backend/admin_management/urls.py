from django.urls import path
from .views import (
    AdminUserListView, AdminUserRecordView, SystemErrorLogView, 
    FrontendErrorLogView, UserStatsView
)

urlpatterns = [
    # 用户管理接口
    path('users/', AdminUserListView.as_view(), name='admin_users'),
    path('users/<int:user_id>/', AdminUserListView.as_view(), name='admin_user_edit'),
    path('users/stats/<int:user_id>/', UserStatsView.as_view(), name='user_stats'),
    
    # 用户记录接口
    path('records/', AdminUserRecordView.as_view(), name='admin_records'),
    path('records/<int:record_id>/', AdminUserRecordView.as_view(), name='admin_record_delete'),
    
    # 系统错误日志接口
    path('error-logs/', SystemErrorLogView.as_view(), name='system_error_logs'),
    
    # 前端错误日志接口
    path('frontend-error-log/', FrontendErrorLogView.as_view(), name='frontend_error_log'),
] 