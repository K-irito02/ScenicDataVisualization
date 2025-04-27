from django.db import migrations

class Migration(migrations.Migration):
    """
    修复迁移问题的迁移文件
    这个迁移用于解决之前迁移中尝试删除不存在的id列的问题
    """
    dependencies = [
        ('scenic_data', '0005_rename_transport_mode_trafficdata_transport_and_more'),
    ]

    operations = [
        # 空操作，仅用于替代之前有问题的迁移
        migrations.RunSQL(
            sql='-- 这是一个空操作，用于替代有问题的迁移',
            reverse_sql='-- 这是空操作的回滚语句'
        ),
    ] 