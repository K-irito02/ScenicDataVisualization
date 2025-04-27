#!/usr/bin/env python
"""
修复迁移问题的辅助脚本
使用方法：
python _fake_migrations.py  # 名称前加下划线表示这不是Django迁移文件
"""

import os
import sys
import django

# 设置Django环境
# 获取当前文件所在目录的父级目录的父级目录（即项目根目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
try:
    django.setup()
except ModuleNotFoundError:
    print("尝试使用备选设置模块...")
    # 如果找不到settings模块，尝试导入backend.settings
    os.environ["DJANGO_SETTINGS_MODULE"] = "backend.settings"
    try:
        django.setup()
    except ModuleNotFoundError:
        print("无法找到Django设置模块，请确保脚本在正确的目录中运行")
        sys.exit(1)

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

def fix_migration_manually():
    """手动修复迁移问题"""
    try:
        # 尝试直接执行SQL来修复迁移记录
        with connection.cursor() as cursor:
            # 检查表是否存在
            cursor.execute("SHOW TABLES LIKE 'django_migrations'")
            if not cursor.fetchone():
                print("django_migrations表不存在，无法继续")
                return False
                
            # 检查有问题的迁移是否存在
            cursor.execute(
                "SELECT id FROM django_migrations WHERE app = 'scenic_data' AND name = '0006_remove_culturalreliclevelprice_id_and_more'"
            )
            result = cursor.fetchone()
            if result:
                # 删除有问题的迁移记录
                cursor.execute(
                    "DELETE FROM django_migrations WHERE app = 'scenic_data' AND name = '0006_remove_culturalreliclevelprice_id_and_more'"
                )
                print("已删除有问题的迁移记录")
            
            # 检查新的修复迁移是否已经存在
            cursor.execute(
                "SELECT id FROM django_migrations WHERE app = 'scenic_data' AND name = '0006_fix_missing_id'"
            )
            result = cursor.fetchone()
            if not result:
                # 添加新的修复迁移记录
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES ('scenic_data', '0006_fix_missing_id', NOW())"
                )
                print("已添加新的修复迁移记录")
            else:
                print("修复迁移记录已存在")
                
            return True
    except Exception as e:
        print(f"手动修复失败: {e}")
        return False

def fake_migration(app, name):
    """将特定迁移标记为已应用"""
    print(f"尝试将迁移 {app}.{name} 标记为已应用...")
    
    # 检查迁移是否已经应用
    recorder = MigrationRecorder(connection)
    applied = recorder.migration_qs.filter(app=app, name=name).exists()
    
    if applied:
        print(f"迁移 {app}.{name} 已经应用过，无需操作")
        return
    
    # 添加迁移记录
    recorder.migration_qs.create(app=app, name=name)
    print(f"已将迁移 {app}.{name} 标记为已应用")

def handle_migration_issues():
    """处理所有迁移问题"""
    try:
        recorder = MigrationRecorder(connection)
        
        # 检查是否存在有问题的迁移记录
        problematic_migrations = [
            ("scenic_data", "0006_remove_culturalreliclevelprice_id_and_more"),
        ]
        
        for app, name in problematic_migrations:
            # 如果有问题的迁移存在，删除它
            if recorder.migration_qs.filter(app=app, name=name).exists():
                print(f"删除有问题的迁移记录: {app}.{name}")
                recorder.migration_qs.filter(app=app, name=name).delete()
        
        # 确保新的修复迁移被标记为已应用
        fake_migration("scenic_data", "0006_fix_missing_id")
        return True
    except Exception as e:
        print(f"处理迁移问题时出错: {e}")
        return False

if __name__ == "__main__":
    print("开始修复迁移问题...")
    
    # 首先尝试使用Django ORM方式修复
    if handle_migration_issues():
        print("使用Django ORM成功修复迁移问题")
    # 如果失败，尝试直接SQL修复
    elif fix_migration_manually():
        print("使用直接SQL成功修复迁移问题")
    else:
        print("修复失败，请手动处理迁移问题")
        sys.exit(1)
    
    print("\n完成! 现在您可以尝试运行:")
    print("python manage.py migrate") 