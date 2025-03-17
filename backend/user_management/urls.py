from django.urls import path
from rest_framework.authtoken import views as token_views
from . import views

urlpatterns = [
    # 用户认证相关
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # 用户资料相关
    path('users/profile/', views.ProfileUpdateView.as_view(), name='profile-update'),
    
    # 用户收藏相关
    path('favorites/toggle/', views.FavoriteToggleView.as_view(), name='favorite-toggle'),
    path('favorites/', views.UserFavoritesView.as_view(), name='user-favorites'),
] 