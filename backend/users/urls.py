from django.urls import path
from . import views
from user_management.views import UploadAvatarView, ProfileUpdateView

"""
用户管理相关的URL配置
可以在这里添加用户登录、注册、个人资料等相关的URL
"""

urlpatterns = [

    # 用户个人资料
    path('profile/', ProfileUpdateView.as_view(), name='profile'),

    # 上传头像
    path('upload-avatar/', UploadAvatarView.as_view(), name='upload-avatar'),

] 