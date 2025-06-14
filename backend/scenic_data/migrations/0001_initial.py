# Generated by Django 5.1.6 on 2025-03-17 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CulturalRelicLevelPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(max_length=50, verbose_name='等级名称')),
                ('count', models.IntegerField(verbose_name='该等级的景区数量')),
                ('average_price', models.FloatField(verbose_name='平均票价')),
                ('min_price', models.FloatField(verbose_name='最低票价')),
                ('max_price', models.FloatField(verbose_name='最高票价')),
                ('median_price', models.FloatField(verbose_name='中位数票价')),
            ],
            options={
                'verbose_name': '文物保护单位等级票价',
                'verbose_name_plural': '文物保护单位等级票价',
                'db_table': 'cultural_relic_level_price',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ForestParkLevelPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(max_length=50, verbose_name='等级名称')),
                ('count', models.IntegerField(verbose_name='该等级的景区数量')),
                ('average_price', models.FloatField(verbose_name='平均票价')),
                ('min_price', models.FloatField(verbose_name='最低票价')),
                ('max_price', models.FloatField(verbose_name='最高票价')),
                ('median_price', models.FloatField(verbose_name='中位数票价')),
            ],
            options={
                'verbose_name': '森林公园等级票价',
                'verbose_name_plural': '森林公园等级票价',
                'db_table': 'forest_park_level_price',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='GeoLogicalParkLevelPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(max_length=50, verbose_name='等级名称')),
                ('count', models.IntegerField(verbose_name='该等级的景区数量')),
                ('average_price', models.FloatField(verbose_name='平均票价')),
                ('min_price', models.FloatField(verbose_name='最低票价')),
                ('max_price', models.FloatField(verbose_name='最高票价')),
                ('median_price', models.FloatField(verbose_name='中位数票价')),
            ],
            options={
                'verbose_name': '地质公园等级票价',
                'verbose_name_plural': '地质公园等级票价',
                'db_table': 'geological_park_level_price',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MuseumLevelPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(max_length=50, verbose_name='等级名称')),
                ('count', models.IntegerField(verbose_name='该等级的景区数量')),
                ('average_price', models.FloatField(verbose_name='平均票价')),
                ('min_price', models.FloatField(verbose_name='最低票价')),
                ('max_price', models.FloatField(verbose_name='最高票价')),
                ('median_price', models.FloatField(verbose_name='中位数票价')),
            ],
            options={
                'verbose_name': '博物馆等级票价',
                'verbose_name_plural': '博物馆等级票价',
                'db_table': 'museum_level_price',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='NatureReserveLevelPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(max_length=50, verbose_name='等级名称')),
                ('count', models.IntegerField(verbose_name='该等级的景区数量')),
                ('average_price', models.FloatField(verbose_name='平均票价')),
                ('min_price', models.FloatField(verbose_name='最低票价')),
                ('max_price', models.FloatField(verbose_name='最高票价')),
                ('median_price', models.FloatField(verbose_name='中位数票价')),
            ],
            options={
                'verbose_name': '自然景区等级票价',
                'verbose_name_plural': '自然景区等级票价',
                'db_table': 'nature_reserve_level_price',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ScenicLevelPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(max_length=50, verbose_name='等级名称')),
                ('count', models.IntegerField(verbose_name='该等级的景区数量')),
                ('average_price', models.FloatField(verbose_name='平均票价')),
                ('min_price', models.FloatField(verbose_name='最低票价')),
                ('max_price', models.FloatField(verbose_name='最高票价')),
                ('median_price', models.FloatField(verbose_name='中位数票价')),
            ],
            options={
                'verbose_name': '景区等级票价',
                'verbose_name_plural': '景区等级票价',
                'db_table': 'scenic_level_price',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WetlandLevelPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(max_length=50, verbose_name='等级名称')),
                ('count', models.IntegerField(verbose_name='该等级的景区数量')),
                ('average_price', models.FloatField(verbose_name='平均票价')),
                ('min_price', models.FloatField(verbose_name='最低票价')),
                ('max_price', models.FloatField(verbose_name='最高票价')),
                ('median_price', models.FloatField(verbose_name='中位数票价')),
            ],
            options={
                'verbose_name': '湿地公园等级票价',
                'verbose_name_plural': '湿地公园等级票价',
                'db_table': 'wetland_level_price',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PriceData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scenic_name', models.CharField(max_length=100, verbose_name='景区名称')),
                ('city_name', models.CharField(max_length=50, verbose_name='所在省份')),
                ('ticket', models.CharField(blank=True, max_length=200, null=True, verbose_name='景区的门票价格')),
            ],
            options={
                'verbose_name': '景区票价数据',
                'verbose_name_plural': '景区票价数据',
                'db_table': 'price_process_django',
            },
        ),
        migrations.CreateModel(
            name='ProvinceTraffic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('province', models.CharField(max_length=50, verbose_name='省份名')),
                ('transport_frequency', models.TextField(blank=True, null=True, verbose_name='交通方式类型出现次数')),
                ('transport_count', models.IntegerField(blank=True, null=True, verbose_name='交通方式类型数量')),
            ],
            options={
                'verbose_name': '省份交通数据',
                'verbose_name_plural': '省份交通数据',
                'db_table': 'province_traffic',
            },
        ),
        migrations.CreateModel(
            name='ScenicData',
            fields=[
                ('scenic_id', models.CharField(db_column='景区ID', max_length=20, primary_key=True, serialize=False, verbose_name='景区ID')),
                ('name', models.CharField(db_column='景区名称', max_length=100, verbose_name='景区名称')),
                ('image_url', models.URLField(blank=True, db_column='图片URL', max_length=500, null=True, verbose_name='图片URL')),
                ('description', models.TextField(blank=True, db_column='景区简介', null=True, verbose_name='景区简介')),
                ('province', models.CharField(blank=True, db_column='所在省份', max_length=50, null=True, verbose_name='所在省份')),
                ('city', models.CharField(blank=True, db_column='所在城市', max_length=50, null=True, verbose_name='所在城市')),
                ('district', models.CharField(blank=True, db_column='所在区县', max_length=50, null=True, verbose_name='所在区县')),
                ('street', models.CharField(blank=True, db_column='所在街道镇乡', max_length=100, null=True, verbose_name='所在街道镇乡')),
                ('coordinates', models.CharField(blank=True, db_column='经纬度', max_length=50, null=True, verbose_name='经纬度')),
                ('scenic_type', models.CharField(blank=True, db_column='景区类型及级别', max_length=200, null=True, verbose_name='景区类型及级别')),
                ('opening_hours', models.TextField(blank=True, db_column='开放时间原数据', null=True, verbose_name='开放时间原数据')),
                ('ticket_price', models.TextField(blank=True, db_column='票价原数据', null=True, verbose_name='票价原数据')),
                ('transportation', models.TextField(blank=True, db_column='交通原数据', null=True, verbose_name='交通原数据')),
                ('comments', models.TextField(blank=True, db_column='评论原数据', null=True, verbose_name='评论原数据')),
                ('min_price', models.IntegerField(blank=True, db_column='最低票价', null=True, verbose_name='最低票价')),
                ('transport_modes', models.CharField(blank=True, db_column='交通方式', max_length=100, null=True, verbose_name='交通方式')),
                ('comment_count', models.IntegerField(blank=True, db_column='评论数量', default=0, null=True, verbose_name='评论数量')),
                ('sentiment', models.CharField(blank=True, db_column='情感倾向', max_length=10, null=True, verbose_name='情感倾向')),
                ('sentiment_score', models.FloatField(blank=True, db_column='情感得分', null=True, verbose_name='情感得分')),
                ('sentiment_intensity', models.FloatField(blank=True, db_column='情感强度', null=True, verbose_name='情感强度')),
                ('high_frequency_words', models.TextField(blank=True, db_column='高频词', null=True, verbose_name='高频词')),
            ],
            options={
                'verbose_name': '景区数据',
                'verbose_name_plural': '景区数据',
                'db_table': 'summary_table',
            },
        ),
        migrations.CreateModel(
            name='TimeData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scenic_name', models.CharField(max_length=100, verbose_name='景区名')),
                ('city_name', models.CharField(max_length=50, verbose_name='省份名')),
                ('time_range', models.CharField(blank=True, max_length=200, null=True, verbose_name='开放时间段')),
            ],
            options={
                'verbose_name': '景区开放时间数据',
                'verbose_name_plural': '景区开放时间数据',
                'db_table': 'time_process',
            },
        ),
        migrations.CreateModel(
            name='TrafficData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transport_mode', models.CharField(max_length=50, verbose_name='交通类型')),
                ('transport_count', models.IntegerField(blank=True, null=True, verbose_name='交通类型出现次数')),
            ],
            options={
                'verbose_name': '交通数据',
                'verbose_name_plural': '交通数据',
                'db_table': 'traffic_add',
            },
        ),
    ]
