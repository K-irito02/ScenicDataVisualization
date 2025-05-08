from django.urls import path
from rest_framework.authtoken import views as token_views
from . import views

urlpatterns = [
    # 用户认证相关
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    
    # 用户资料相关
    path('users/profile/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('users/upload-avatar/', views.UploadAvatarView.as_view(), name='upload-avatar'),
    path('users/delete-account/', views.DeleteAccountView.as_view(), name='delete-account'),
    
    # 用户收藏相关
    path('favorites/toggle/', views.FavoriteToggleView.as_view(), name='favorite-toggle'),
    path('favorites/', views.UserFavoritesView.as_view(), name='user-favorites'),
    
    # 验证码相关
    path('email/send-code/', views.SendEmailCodeView.as_view(), name='send-email-code'),
    path('email/verify-code/', views.VerifyEmailCodeView.as_view(), name='verify-email-code'),
] 