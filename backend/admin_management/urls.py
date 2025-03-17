from django.urls import path
from . import views

urlpatterns = [
    # 用户管理接口
    path('admin/users/', views.AdminUserListView.as_view(), name='admin-users'),
    
    # 用户记录接口
    path('admin/user-records/', views.AdminUserRecordView.as_view(), name='admin-user-records'),
] 