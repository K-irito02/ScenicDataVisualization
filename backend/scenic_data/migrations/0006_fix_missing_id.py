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
        # 使用虚拟操作替代空SQL
        migrations.RunSQL(
            sql='SELECT 1;',
            reverse_sql='SELECT 1;'
        ),
    ] 