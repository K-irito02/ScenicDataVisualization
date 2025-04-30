from django.urls import path
from . import views
from user_management.views import UploadAvatarView, ProfileUpdateView

"""
用户管理相关的URL配置
用户上传头像、个人资料的URL
"""

urlpatterns = [

    # 用户个人资料
    path('profile/', ProfileUpdateView.as_view(), name='profile'),

    # 上传头像
    path('upload-avatar/', UploadAvatarView.as_view(), name='upload-avatar'),

] 