from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, UserFavorite, UserActionRecord
from django.contrib.auth import authenticate
from .utils import redis_client

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)

class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('user', 'avatar', 'location', 'last_login')

class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("用户已被禁用")
                data['user'] = user
            else:
                raise serializers.ValidationError("用户名或密码错误")
        else:
            raise serializers.ValidationError("必须同时提供用户名和密码")
        
        return data

class RegisterSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        min_length=6,
        error_messages={
            'min_length': '密码长度不能少于6个字符'
        }
    )
    code = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'code')
        error_messages = {
            'username': {
                'unique': '该用户名已被使用',
                'required': '请输入用户名',
                'blank': '用户名不能为空'
            },
            'email': {
                'unique': '该邮箱已被注册',
                'required': '请输入邮箱地址',
                'blank': '邮箱地址不能为空',
                'invalid': '请输入有效的邮箱地址'
            }
        }
    
    def validate_code(self, value):
        email = self.initial_data.get('email')
        print(f"验证码验证 - 邮箱: {email}, 输入的验证码: {value}")
        
        if not email:
            raise serializers.ValidationError("请先输入邮箱地址")
        
        # 从Redis获取验证码
        redis_key = f'email_code:{email}'
        stored_code = redis_client.get(redis_key)
        print(f"Redis中的验证码: {stored_code}")
        
        if not stored_code:
            print(f"Redis中不存在该邮箱的验证码: {redis_key}")
            raise serializers.ValidationError("验证码已过期，请重新获取")
        
        print(f"验证码比较: 输入={value}, 存储={stored_code}")
        
        if value != stored_code:
            print(f"验证码不匹配: 输入={value}, 存储={stored_code}")
            raise serializers.ValidationError("验证码错误")
        
        # 验证成功后删除验证码
        redis_client.delete(redis_key)
        print(f"验证码验证成功，已从Redis中删除: {redis_key}")
        return value
    
    def create(self, validated_data):
        print(f"创建用户 - 数据: {validated_data}")
        try:
            # 移除验证码字段
            validated_data.pop('code')
            
            # 检查用户名是否已存在
            if User.objects.filter(username=validated_data['username']).exists():
                raise serializers.ValidationError({'username': ['该用户名已被使用']})
            
            # 检查邮箱是否已存在
            if User.objects.filter(email=validated_data['email']).exists():
                raise serializers.ValidationError({'email': ['该邮箱已被注册']})
            
            # 创建用户
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password']
            )
            print(f"用户创建成功: {user.username}")
            
            # 创建用户资料
            try:
                UserProfile.objects.create(user=user)
                print(f"用户资料创建成功: {user.username}")
            except Exception as e:
                print(f"用户资料创建失败: {str(e)}")
                # 如果创建资料失败，删除已创建的用户
                user.delete()
                raise serializers.ValidationError({'profile': ['创建用户资料失败']})
            
            return user
        except Exception as e:
            print(f"用户创建失败: {str(e)}")
            raise

class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""
    class Meta:
        model = User
        fields = ('username', 'email')
        
class ProfileUpdateSerializer(serializers.ModelSerializer):
    """用户资料更新序列化器"""
    username = serializers.CharField(source='user.username', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'avatar', 'location')
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        # 更新User模型字段
        if 'username' in user_data:
            user.username = user_data['username']
        if 'email' in user_data:
            user.email = user_data['email']
        user.save()
        
        # 更新UserProfile模型字段
        if 'avatar' in validated_data:
            instance.avatar = validated_data['avatar']
        if 'location' in validated_data:
            instance.location = validated_data['location']
        instance.save()
        
        return instance

class UserFavoriteSerializer(serializers.ModelSerializer):
    """用户收藏序列化器"""
    class Meta:
        model = UserFavorite
        fields = ('id', 'user', 'scenic_id', 'added_time')
        read_only_fields = ('id', 'user', 'added_time')

class UserActionRecordSerializer(serializers.ModelSerializer):
    """用户操作记录序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserActionRecord
        fields = ('id', 'user', 'username', 'action_type', 'details', 'timestamp')
        read_only_fields = ('id', 'user', 'username', 'timestamp') 