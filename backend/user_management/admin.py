from django.contrib import admin
from .models import UserProfile, UserFavorite, UserActionRecord

# 注册用户资料模型
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar', 'location', 'last_login']
    search_fields = ['user__username', 'location']
    list_filter = ['last_login']

# 注册用户收藏模型
@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'scenic_id', 'added_time']
    search_fields = ['user__username', 'scenic_id']
    list_filter = ['added_time']

# 注册用户操作记录模型
@admin.register(UserActionRecord)
class UserActionRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'details', 'timestamp']
    search_fields = ['user__username', 'action_type', 'details']
    list_filter = ['action_type', 'timestamp']
