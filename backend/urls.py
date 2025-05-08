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

# 创建Django管理站点的另一个实例
admin_django_site = admin.AdminSite(name='django_admin')
admin_django_site.site_header = 'Django 管理后台'
admin_django_site.site_title = 'Django 管理后台'
admin_django_site.index_title = 'Django 管理后台'

# 注册模型到Django原生管理站点
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
admin_django_site.register(User, UserAdmin)
admin_django_site.register(Group, GroupAdmin)

# 注册用户管理相关模型
from user_management.models import UserProfile, UserFavorite, UserActionRecord
# 创建admin类，与user_management/admin.py中定义的一致
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar', 'location', 'last_login']
    search_fields = ['user__username', 'location']
    list_filter = ['last_login']

class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'scenic_id', 'added_time']
    search_fields = ['user__username', 'scenic_id']
    list_filter = ['added_time']

class UserActionRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'details', 'timestamp']
    search_fields = ['user__username', 'action_type', 'details']
    list_filter = ['action_type', 'timestamp']

admin_django_site.register(UserProfile, UserProfileAdmin)
admin_django_site.register(UserFavorite, UserFavoriteAdmin)
admin_django_site.register(UserActionRecord, UserActionRecordAdmin)

# 注册景区数据相关模型
from scenic_data.models import (
    ScenicData, PriceData, ProvinceTraffic, TrafficData, TimeData,
    ScenicLevelPrice, MuseumLevelPrice, GeoLogicalParkLevelPrice,
    ForestParkLevelPrice, WetlandLevelPrice, CulturalRelicLevelPrice,
    NatureReserveLevelPrice, TransportMode
)
admin_django_site.register(ScenicData)
admin_django_site.register(PriceData)
admin_django_site.register(ProvinceTraffic)
admin_django_site.register(TrafficData)
admin_django_site.register(TimeData)
admin_django_site.register(ScenicLevelPrice)
admin_django_site.register(MuseumLevelPrice)
admin_django_site.register(GeoLogicalParkLevelPrice)
admin_django_site.register(ForestParkLevelPrice)
admin_django_site.register(WetlandLevelPrice)
admin_django_site.register(CulturalRelicLevelPrice)
admin_django_site.register(NatureReserveLevelPrice)
admin_django_site.register(TransportMode)

# 注册管理员模块模型
from admin_management.models import SystemErrorLog
# 创建admin类，与admin_management/admin.py中定义的一致
class SystemErrorLogAdmin(admin.ModelAdmin):
    list_display = ('level', 'message', 'path', 'user_id', 'ip_address', 'timestamp')
    list_filter = ('level', 'timestamp')
    search_fields = ('message', 'path', 'ip_address')
    readonly_fields = ('level', 'message', 'traceback', 'path', 'method', 'user_id', 'ip_address', 'timestamp')
    ordering = ('-timestamp',)

admin_django_site.register(SystemErrorLog, SystemErrorLogAdmin)

# 注册Token模型
from rest_framework.authtoken.models import Token
admin_django_site.register(Token)

urlpatterns = [
    # 管理界面
    path('admin/', admin.site.urls),  # 项目自定义管理界面
    path('django_admin/', admin_django_site.urls),  # Django原生管理界面的新URL
    
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
else:
    # 在生产环境中也提供媒体文件访问
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
