"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from scenic_data.models import ScenicData
from django.db.models import Q
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 管理界面
    path('admin/', admin.site.urls),
    
    # API接口 - 用户管理（认证和收藏）
    path('api/', include('user_management.urls')),
    
    # API接口 - 景区数据
    path('api/', include('scenic_data.urls')),
    
    # API接口 - 用户资料和头像
    path('api/users/', include('users.urls')),
    
    # API接口 - 管理员功能
    path('api/admin/', include('admin_management.urls')), 
]

# 添加媒体文件URL配置
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
