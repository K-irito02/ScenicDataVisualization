# Generated by Django 5.1.6 on 2025-04-15 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scenic_data', '0002_rename_sentiment_intensity_scenicdata_sentiment_magnitude_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timedata',
            name='type',
        ),
        migrations.AddField(
            model_name='timedata',
            name='date_range',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='日期范围'),
        ),
        migrations.AddField(
            model_name='timedata',
            name='is_24h',
            field=models.BooleanField(default=False, verbose_name='是否24小时开放'),
        ),
        migrations.AddField(
            model_name='timedata',
            name='is_closed',
            field=models.BooleanField(default=False, verbose_name='是否关闭'),
        ),
        migrations.AddField(
            model_name='timedata',
            name='is_holiday',
            field=models.BooleanField(default=False, verbose_name='是否节假日'),
        ),
        migrations.AddField(
            model_name='timedata',
            name='season',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='季节'),
        ),
        migrations.AddField(
            model_name='timedata',
            name='stop_ticket_time',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='停止售票时间'),
        ),
        migrations.AlterField(
            model_name='timedata',
            name='city_name',
            field=models.CharField(max_length=50, verbose_name='城市名'),
        ),
        migrations.AlterField(
            model_name='timedata',
            name='scenic_id',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='景区ID'),
        ),
    ]
