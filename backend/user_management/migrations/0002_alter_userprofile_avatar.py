# Generated by Django 5.1.6 on 2025-04-15 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='头像路径'),
        ),
    ]
