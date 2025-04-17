from django.urls import path
from . import views

urlpatterns = [
    # 用户管理接口
    path('users/', views.AdminUserListView.as_view(), name='admin-users'),
    path('users/<int:user_id>/', views.AdminUserListView.as_view(), name='admin-user-detail'),
    
    # 用户记录接口
    path('user-records/', views.AdminUserRecordView.as_view(), name='admin-user-records'),
    path('user-records/<int:record_id>/', views.AdminUserRecordView.as_view(), name='admin-user-record-detail'),
    
    # 系统错误日志接口
    path('error-logs/', views.SystemErrorLogView.as_view(), name='admin-error-logs'),
    
    # 前端错误日志接口
    path('frontend-error/', views.FrontendErrorLogView.as_view(), name='frontend-error-log'),
] 