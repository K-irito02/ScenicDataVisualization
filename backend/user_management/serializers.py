from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, UserFavorite, UserActionRecord
from django.contrib.auth import authenticate

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
        min_length=6
    )
    code = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'code')
    
    def validate_code(self, value):
        # 这里可以添加验证码验证逻辑
        # 简单实现，可以设置一个固定验证码或接入验证码服务
        if value != '123456':  # 示例，实际使用中应换成真实验证逻辑
            raise serializers.ValidationError("验证码无效")
        return value
    
    def create(self, validated_data):
        validated_data.pop('code')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        return user

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