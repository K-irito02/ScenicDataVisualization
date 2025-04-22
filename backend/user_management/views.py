from django.shortcuts import render
from rest_framework import status, viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
import random
from .utils import redis_client  # 从utils导入redis_client

from .models import UserProfile, UserFavorite, UserActionRecord
from django.contrib.auth.models import User
from .serializers import (
    LoginSerializer, RegisterSerializer, UserProfileSerializer,
    ProfileUpdateSerializer, UserFavoriteSerializer
)

class LoginView(APIView):
    """用户登录视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.validated_data['user']
                
                # 检查用户是否被禁用
                if not user.is_active:
                    # 明确返回禁用用户错误状态
                    return Response(
                        {'detail': '用户已被禁用', 'message': '您的账号已被管理员禁用，请联系管理员'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # 更新最后登录时间
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.last_login = timezone.now()
                profile.save()
                
                # 记录登录操作
                UserActionRecord.objects.create(
                    user=user,
                    action_type='login',
                    details='用户登录'
                )
                
                # 获取或创建令牌
                token, created = Token.objects.get_or_create(user=user)
                
                # 准备响应数据
                response_data = {
                    'token': token.key,
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'avatar': profile.avatar,
                    'location': profile.location,
                    'is_admin': user.is_staff
                }
                
                return Response(response_data)
            
            # 序列化器验证失败的情况
            # 提取错误信息，检查是否包含"用户已被禁用"
            error_message = ''
            if serializer.errors.get('non_field_errors'):
                for error in serializer.errors['non_field_errors']:
                    if '用户已被禁用' in str(error):
                        # 对于禁用用户，返回明确的403错误
                        return Response(
                            {'detail': '用户已被禁用', 'message': '您的账号已被管理员禁用，请联系管理员'}, 
                            status=status.HTTP_403_FORBIDDEN
                        )
                    error_message = error
            
            # 其他登录错误
            return Response(
                {'detail': error_message or '登录失败', 'errors': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"登录过程发生异常: {str(e)}\n{error_detail}")
            
            # 特别检查是否是由用户禁用状态导致的错误
            if 'is_active' in str(e).lower() or '已被禁用' in str(e):
                return Response(
                    {'detail': '用户已被禁用', 'message': '您的账号已被管理员禁用，请联系管理员'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 通用的服务器错误
            return Response(
                {'detail': '登录失败', 'message': f'服务器处理请求时出错: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegisterView(APIView):
    """用户注册视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        try:
            if serializer.is_valid():
                user = serializer.save()
                
                # 记录注册操作
                UserActionRecord.objects.create(
                    user=user,
                    action_type='register',
                    details='用户注册'
                )
                
                return Response({
                    'success': True,
                    'message': '注册成功'
                }, status=status.HTTP_201_CREATED)
            else:
                print(f"数据验证失败，错误信息: {serializer.errors}")
                return Response({
                    'success': False,
                    'message': '注册失败',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"注册过程发生异常: {str(e)}")
            return Response({
                'success': False,
                'message': f'注册失败: {str(e)}',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileUpdateView(APIView):
    """用户资料更新视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        try:
            
            # 使用更可靠的方法获取或创建profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                
                # 记录更新操作
                UserActionRecord.objects.create(
                    user=request.user,
                    action_type='profile_update',
                    details='更新个人资料'
                )
                
                # 准备响应数据
                user = request.user
                return Response({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'avatar': profile.avatar,
                        'location': profile.location,
                        'isAdmin': user.is_staff
                    }
                })
            
            # 详细记录验证错误
            print(f"用户资料更新验证失败: {serializer.errors}")
            
            # 特别检查avatar字段错误
            if 'avatar' in serializer.errors:
                print(f"Avatar字段错误: {serializer.errors['avatar']}")
                
                # 如果是URL验证错误，提供更具体的帮助信息
                if any('有效的URL' in str(err) for err in serializer.errors['avatar']):
                    serializer.errors['avatar'].append("头像URL必须是有效的URL格式，请提供合法的URL路径")
            
            return Response({
                'success': False,
                'errors': serializer.errors,
                'message': '资料更新失败，请检查提交的数据'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"处理用户资料更新时发生异常: {str(e)}\n{error_detail}")
            
            return Response({
                'success': False,
                'message': f'服务器处理请求时出错: {str(e)}',
                'error_type': e.__class__.__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FavoriteToggleView(APIView):
    """景区收藏切换视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        scenic_id = request.data.get('scenic_id')
        if not scenic_id:
            return Response({
                'success': False,
                'message': '缺少景区ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            favorite, created = UserFavorite.objects.get_or_create(
                user=request.user,
                scenic_id=scenic_id
            )
            
            if not created:
                # 如果已存在，则取消收藏
                favorite.delete()
                is_favorite = False
                action_details = f'取消收藏景区(ID: {scenic_id})'
            else:
                is_favorite = True
                action_details = f'收藏景区(ID: {scenic_id})'
            
            # 记录收藏操作
            UserActionRecord.objects.create(
                user=request.user,
                action_type='favorite',
                details=action_details
            )
            
            return Response({
                'success': True,
                'is_favorite': is_favorite
            })

class UserFavoritesView(generics.ListAPIView):
    """用户收藏列表视图"""
    serializer_class = UserFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user)

class UploadAvatarView(APIView):
    """用户头像上传视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            
            avatar_file = request.FILES.get('avatar')
            
            if not avatar_file:
                print("错误: 未提供头像文件")
                return Response({
                    'success': False,
                    'message': '未提供头像文件'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 文件大小限制(5MB)
            if avatar_file.size > 5 * 1024 * 1024:
                return Response({
                    'success': False,
                    'message': '文件大小不能超过5MB'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查文件类型
            valid_types = ['image/jpeg', 'image/png', 'image/gif']
            if avatar_file.content_type not in valid_types:
                return Response({
                    'success': False,
                    'message': f'只支持JPEG、PNG或GIF格式的图片，当前类型: {avatar_file.content_type}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 上传到静态文件目录
            import os
            import uuid
            from django.conf import settings
            
            # 确保媒体根目录存在
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            
            # 创建用户媒体目录
            user_media_dir = os.path.join(settings.MEDIA_ROOT, f'avatars/user_{request.user.id}')
            os.makedirs(user_media_dir, exist_ok=True)
            
            # 删除用户之前的头像文件（可选）
            try:
                # 查找用户之前的头像
                profile = request.user.profile
                if profile.avatar:
                    # 处理相对路径和绝对路径两种情况
                    if profile.avatar.startswith('/media/'):
                        old_path = os.path.join(settings.MEDIA_ROOT, profile.avatar.lstrip('/media/'))
                    elif profile.avatar.startswith('media/'):
                        old_path = os.path.join(settings.MEDIA_ROOT, profile.avatar.lstrip('media/'))
                    else:
                        # 其他情况，例如外部URL，则跳过删除
                        old_path = None
                    
                    if old_path and os.path.exists(old_path):
                        os.remove(old_path)
            except Exception as e:
                print(f"删除旧头像文件失败: {str(e)}")
                # 继续处理，不中断上传流程
            
            # 生成唯一文件名，确保每次上传都用不同的文件名
            import time
            random_uuid = uuid.uuid4().hex[:8]  # 生成8位随机UUID
            timestamp = int(time.time())
            file_ext = avatar_file.name.split('.')[-1]
            file_name = f"avatar_{timestamp}_{random_uuid}.{file_ext}"
            file_path = os.path.join(user_media_dir, file_name)
            
            # 保存文件
            with open(file_path, 'wb+') as destination:
                for chunk in avatar_file.chunks():
                    destination.write(chunk)
            
            # 更新用户头像URL
            avatar_url = f"/media/avatars/user_{request.user.id}/{file_name}"
            print(f"设置的头像URL: {avatar_url}")
            
            try:
                profile = request.user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=request.user)
            
            profile.avatar = avatar_url
            profile.save()
            
            # 记录上传操作
            UserActionRecord.objects.create(
                user=request.user,
                action_type='profile_update',
                details='上传头像'
            )
            
            
            return Response({
                'success': True,
                'avatar_url': avatar_url,
                'full_url': request.build_absolute_uri(avatar_url)  # 添加返回完整URL
            })
            
        except Exception as e:
            print(f"头像上传失败: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'message': f'头像上传失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendEmailCodeView(APIView):
    """发送邮箱验证码视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        email = request.data.get('email')
        if not email:
            return Response({
                'success': False,
                'message': '请提供邮箱地址'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查邮箱是否已被注册
        try:
            if User.objects.filter(email=email).exists():
                return Response({
                    'success': False,
                    'message': '该邮箱已被使用'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"检查邮箱是否已存在时出错: {str(e)}")
        
        # 生成6位随机验证码
        code = ''.join(random.choices('0123456789', k=6))
        
        try:
            logger.info(f"准备为邮箱 {email} 生成验证码")
            
            # 首先尝试保存验证码到Redis
            redis_key = f'email_code:{email}'
            try:
                redis_client.setex(redis_key, 300, code)
                logger.info(f"验证码已保存到Redis: {email}")
            except Exception as redis_error:
                logger.error(f"Redis保存验证码失败: {str(redis_error)}")
                return Response({
                    'success': False,
                    'message': '验证码生成失败，请稍后重试'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
            # 在单独的try-except块中处理邮件发送
            try:
                from django.core.mail import EmailMessage
                email_message = EmailMessage(
                    subject='景区数据分析系统 - 验证码',
                    body=f'您的验证码是：{code}，有效期为5分钟。请勿将验证码泄露给他人。',
                    from_email=settings.EMAIL_HOST_USER,
                    to=[email]
                )
                email_message.send(fail_silently=False)
                logger.info(f"邮件已发送到 {email}")
            except Exception as email_error:
                logger.error(f"邮件发送失败: {str(email_error)}")
                # 尽管邮件发送失败，但验证码已保存到Redis
                # 在实际生产环境中可能需要返回错误，但为了方便测试，我们仍返回成功
                if settings.DEBUG:
                    return Response({
                        'success': True,
                        'message': '验证码已生成但邮件发送失败，请查看服务器日志获取验证码',
                        'debug_code': code if settings.DEBUG else None
                    })
                else:
                    return Response({
                        'success': False,
                        'message': '邮件发送失败，请稍后重试'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 邮件发送成功，返回成功响应
            return Response({
                'success': True,
                'message': '验证码已发送，请查收邮件'
            })
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"验证码处理过程发生异常: {str(e)}\n{error_details}")
            
            return Response({
                'success': False,
                'message': '验证码发送失败，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteAccountView(APIView):
    """用户删除账户视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        password = request.data.get('password')
        
        if not password:
            return Response({
                'success': False,
                'message': '请提供密码以确认删除操作'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证用户密码
        if not user.check_password(password):
            return Response({
                'success': False,
                'message': '密码不正确，无法删除账户'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 删除与该用户相关的所有数据
            with transaction.atomic():
                # 删除用户的token
                Token.objects.filter(user=user).delete()
                
                # 删除用户的收藏记录
                UserFavorite.objects.filter(user=user).delete()
                
                # 删除用户的行为记录
                UserActionRecord.objects.filter(user=user).delete()
                
                # 记录一条账户删除的操作记录（虽然马上也会被删除）
                UserActionRecord.objects.create(
                    user=user,
                    action_type='delete_account',
                    details='用户删除自己的账户'
                )
                
                # 删除用户的个人资料
                try:
                    if hasattr(user, 'profile'):
                        user.profile.delete()
                except Exception as e:
                    print(f"删除用户资料时出错: {str(e)}")
                
                # 最后删除用户账户
                user.delete()
                
            return Response({
                'success': True,
                'message': '账户已成功删除'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'删除账户时出错: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForgotPasswordView(APIView):
    """忘记密码视图 - 发送重置密码验证码"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        
        email = request.data.get('email')
        if not email:
            return Response({
                'success': False,
                'message': '请提供邮箱地址'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
        # 检查邮箱是否存在
        try:
            user = User.objects.get(email=email)
            print(f"找到用户: {user.username}")
        except User.DoesNotExist:
            print(f"用户不存在: {email}")
            # 为了安全起见，我们不告诉用户邮箱不存在
            
            return Response({
                'success': True,
                'message': '如果该邮箱已注册，我们已发送重置密码的验证码'
            })
        except User.MultipleObjectsReturned:
            return Response({
                'success': False,
                'message': '该邮箱已被多个账户使用，请联系管理员处理'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成6位随机验证码
        code = ''.join(random.choices('0123456789', k=6))
        
        try:
            # 首先尝试保存验证码到Redis，使用不同的前缀区分注册和重置密码
            redis_key = f'reset_password_code:{email}'
            try:
                
                # 设置5分钟有效期
                redis_client.setex(redis_key, 300, code)
            except Exception as redis_error:
                print(f"Redis操作失败: {str(redis_error)}")
                import traceback
                print(f"Redis错误详情: {traceback.format_exc()}")
                return Response({
                    'success': False,
                    'message': '验证码生成失败，请检查Redis服务是否正常运行'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 在单独的try-except块中处理邮件发送
            try:
                from django.core.mail import EmailMessage
                email_message = EmailMessage(
                    subject='景区数据分析系统 - 重置密码验证码',
                    body=f'您的重置密码验证码是：{code}，有效期为5分钟。请勿将验证码泄露给他人。如果这不是您的操作，请忽略此邮件。',
                    from_email=settings.EMAIL_HOST_USER,
                    to=[email]
                )
                email_message.send(fail_silently=False)
            except Exception as email_error:
                print(f"邮件发送失败: {str(email_error)}")
                import traceback
                print(f"邮件发送错误详情: {traceback.format_exc()}")
                # 尽管邮件发送失败，但验证码已保存到Redis
                if settings.DEBUG:
                    return Response({
                        'success': True,
                        'message': '验证码已生成但邮件发送失败，请查看服务器日志获取验证码',
                        'debug_code': code if settings.DEBUG else None
                    })
                else:
                    return Response({
                        'success': False,
                        'message': '邮件发送失败，请稍后重试'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 记录重置密码尝试
            try:
                UserActionRecord.objects.create(
                    user=user,
                    action_type='reset_password_request',
                    details='请求重置密码验证码'
                )
            except Exception as e:
                print(f"记录重置密码操作失败: {str(e)}")
                # 忽略记录失败，继续流程
            
            # 邮件发送成功，返回成功响应
            return Response({
                'success': True,
                'message': '验证码已发送，请查收邮件'
            })
            
        except Exception as e:
            print(f"处理过程中发生未捕获异常: {str(e)}")
            import traceback
            error_details = traceback.format_exc()
            print(f"异常详情: {error_details}")
            
            return Response({
                'success': False,
                'message': '验证码发送失败，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResetPasswordView(APIView):
    """重置密码视图 - 验证验证码并重置密码"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('password')
        
        if not all([email, code, new_password]):
            return Response({
                'success': False,
                'message': '请提供邮箱、验证码和新密码'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查密码长度
        if len(new_password) < 6:
            return Response({
                'success': False,
                'message': '密码长度不能少于6个字符'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证验证码
        redis_key = f'reset_password_code:{email}'
        stored_code = redis_client.get(redis_key)
        
        logger.info(f"验证重置密码验证码 - 邮箱: {email}, 输入的验证码: {code}, 存储的验证码: {stored_code}")
        
        if not stored_code or stored_code != code:
            return Response({
                'success': False,
                'message': '验证码错误或已过期，请重新获取'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 查找用户
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': '邮箱不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.MultipleObjectsReturned:
            return Response({
                'success': False,
                'message': '该邮箱已被多个账户使用，请联系管理员处理'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 重置密码
        try:
            user.set_password(new_password)
            user.save()
            
            # 删除验证码
            redis_client.delete(redis_key)
            
            # 记录密码重置操作
            UserActionRecord.objects.create(
                user=user,
                action_type='reset_password',
                details='密码重置成功'
            )
            
            return Response({
                'success': True,
                'message': '密码重置成功，请使用新密码登录'
            })
        except Exception as e:
            logger.error(f"重置密码失败: {str(e)}")
            return Response({
                'success': False,
                'message': '密码重置失败，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
