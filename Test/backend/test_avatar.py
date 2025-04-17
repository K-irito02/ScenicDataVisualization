"""
测试头像生成脚本，验证文件名生成逻辑
"""

import os
import time
import uuid
from django.conf import settings

def test_avatar_path():
    """测试头像路径生成逻辑"""
    # 模拟文件名生成
    timestamp = int(time.time())
    random_uuid = uuid.uuid4().hex[:8]
    file_ext = "jpg"
    file_name = f"avatar_{timestamp}_{random_uuid}.{file_ext}"
    
    # 打印结果
    print(f"生成的文件名: {file_name}")
    print(f"时间戳部分: {timestamp}")
    print(f"UUID部分: {random_uuid}")
    
    # 构建完整路径
    user_id = 1  # 测试用户ID
    media_root = getattr(settings, 'MEDIA_ROOT', '/tmp')
    user_media_dir = os.path.join(media_root, f'avatars/user_{user_id}')
    file_path = os.path.join(user_media_dir, file_name)
    avatar_url = f"/media/avatars/user_{user_id}/{file_name}"
    
    print(f"用户媒体目录: {user_media_dir}")
    print(f"文件完整路径: {file_path}")
    print(f"头像URL: {avatar_url}")
    
    return avatar_url

if __name__ == "__main__":
    # 在Django之外运行
    class DummySettings:
        MEDIA_ROOT = "./media"
    
    settings = DummySettings()
    test_avatar_path() 