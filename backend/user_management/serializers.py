from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, UserFavorite, UserActionRecord
from django.contrib.auth import authenticate
from .utils import redis_client
from django.core.validators import URLValidator

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
    username_or_email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    def validate(self, data):
        username_or_email = data.get('username_or_email')
        password = data.get('password')
        
        if not username_or_email or not password:
            raise serializers.ValidationError("必须同时提供用户名/邮箱和密码")
        
        # 先尝试以用户名查找用户
        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            # 如果按用户名找不到，尝试按邮箱查找
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                # 既不是有效的用户名也不是有效的邮箱
                raise serializers.ValidationError("用户名/邮箱或密码错误")
        
        # 先检查用户是否被禁用
        if not user.is_active:
            raise serializers.ValidationError("用户已被禁用")
        
        # 再验证密码
        if not user.check_password(password):
            raise serializers.ValidationError("用户名/邮箱或密码错误")
        
        # 认证通过，将用户添加到验证数据中
        data['user'] = user
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
    
    def validate_email(self, value):
        """验证邮箱是否已存在"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被使用")
        return value
    
    def validate_code(self, value):
        email = self.initial_data.get('email')
        
        if not email:
            raise serializers.ValidationError("请先输入邮箱地址")
        
        # 从Redis获取验证码
        redis_key = f'email_code:{email}'
        stored_code = redis_client.get(redis_key)
        
        if not stored_code:
            raise serializers.ValidationError("验证码已过期，请重新获取")
        
        
        if value != stored_code:
            raise serializers.ValidationError("验证码错误")
        
        # 不在此处删除验证码，而是在create方法成功后删除
        # 将验证码保存在实例中，供create方法使用
        self._redis_key = redis_key
        return value
    
    def create(self, validated_data):
        try:
            # 移除验证码字段
            validated_data.pop('code')
            
            # 不再重复检查用户名和邮箱，因为Model已有唯一性约束，会自动抛出异常
            
            # 创建用户
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password']
            )
            
            # 创建用户资料
            try:
                UserProfile.objects.create(user=user)
            except Exception as e:
                print(f"用户资料创建失败: {str(e)}")
                # 如果创建资料失败，删除已创建的用户
                user.delete()
                raise serializers.ValidationError({'profile': ['创建用户资料失败']})
            
            # 验证成功且用户创建成功后，才删除Redis中的验证码
            try:
                if hasattr(self, '_redis_key'):
                    redis_client.delete(self._redis_key)
            except Exception as e:
                print(f"删除Redis验证码失败: {str(e)}")
                # 验证码删除失败不阻止用户创建
            
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
    email_code = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'email_code', 'avatar', 'location')
    
    def validate(self, data):
        """验证当邮箱变更时，需要验证码"""
        user_data = data.get('user', {})
        email = user_data.get('email')
        email_code = data.pop('email_code', None)
        
        # 获取当前用户的邮箱
        current_user = self.instance.user
        current_email = current_user.email if current_user else None
        
        # 如果正在修改邮箱地址
        if email and current_email and email != current_email:
            if not email_code:
                raise serializers.ValidationError({"email_code": ["修改邮箱地址需要验证码"]})
            
            # 从Redis获取验证码
            from .utils import redis_client
            redis_key = f'email_code:{email}'
            stored_code = redis_client.get(redis_key)
            
            if not stored_code:
                raise serializers.ValidationError({"email_code": ["验证码已过期，请重新获取"]})
            
            if email_code != stored_code:
                raise serializers.ValidationError({"email_code": ["验证码错误"]})
            
            # 验证码正确，删除Redis中的验证码
            try:
                redis_client.delete(redis_key)
            except Exception as e:
                print(f"删除Redis验证码失败: {str(e)}")
        
        return data
    
    def validate_avatar(self, value):
        """验证并处理avatar URL"""
        if not value:
            return value
        
        # 如果是完整URL，直接返回
        if value.startswith('http://') or value.startswith('https://'):
            return value
        
        # 如果是相对路径，确保以/media/开头
        if not value.startswith('/media/'):
            if value.startswith('media/'):
                value = '/' + value
            elif not value.startswith('/'):
                value = '/media/' + value
                
        return value
    
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
    # 添加景区详细信息
    id = serializers.CharField(source='scenic_id')
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    
    class Meta:
        model = UserFavorite
        fields = ('id', 'name', 'image', 'province', 'city', 'level', 'added_time')
    
    def get_name(self, obj):
        # 从ScenicData中获取景区名称
        from scenic_data.models import ScenicData
        try:
            scenic = ScenicData.objects.get(scenic_id=obj.scenic_id)
            return scenic.name
        except ScenicData.DoesNotExist:
            return f"未知景区({obj.scenic_id})"
    
    def get_image(self, obj):
        # 从ScenicData中获取景区图片
        from scenic_data.models import ScenicData
        try:
            scenic = ScenicData.objects.get(scenic_id=obj.scenic_id)
            return scenic.image_url or '/static/images/default-scenic.jpg'
        except ScenicData.DoesNotExist:
            return '/static/images/default-scenic.jpg'
    
    def get_province(self, obj):
        # 从ScenicData中获取景区省份
        from scenic_data.models import ScenicData
        try:
            scenic = ScenicData.objects.get(scenic_id=obj.scenic_id)
            return scenic.province
        except ScenicData.DoesNotExist:
            return '未知'
    
    def get_city(self, obj):
        # 从ScenicData中获取景区城市
        from scenic_data.models import ScenicData
        try:
            scenic = ScenicData.objects.get(scenic_id=obj.scenic_id)
            return scenic.city
        except ScenicData.DoesNotExist:
            return '未知'
    
    def get_level(self, obj):
        # 从ScenicData中获取景区级别
        from scenic_data.models import ScenicData
        try:
            scenic = ScenicData.objects.get(scenic_id=obj.scenic_id)
            return scenic.scenic_type.split(',')[0] if scenic.scenic_type else '暂无分类'
        except (ScenicData.DoesNotExist, IndexError):
            return '暂无分类'

class UserActionRecordSerializer(serializers.ModelSerializer):
    """用户操作记录序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserActionRecord
        fields = ('id', 'user', 'username', 'action_type', 'details', 'timestamp')
        read_only_fields = ('id', 'user', 'username', 'timestamp') 