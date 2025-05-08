from django.core.management.base import BaseCommand
from django.db import connections
import logging
import MySQLdb

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '将hierarchy_ticketanalysis数据库中的表迁移到scenic_area数据库'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只检查要迁移的表，不实际执行迁移',
        )
        
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # 定义源数据库和目标数据库的连接参数
        SOURCE_DB = {
            'name': 'hierarchy_ticketanalysis',
            'user': 'root',  # 替换为您的数据库用户名
            'password': '3143285505',  # 替换为您的数据库密码
            'host': 'localhost',
            'port': 3306
        }

        TARGET_DB = {
            'name': 'scenic_area',
            'user': 'root',  # 替换为您的数据库用户名
            'password': '3143285505',  # 替换为您的数据库密码
            'host': 'localhost',
            'port': 3306
        }
        
        # 要迁移的表列表
        TABLES = [
            'scenic_level_price',
            'museum_level_price',
            'geological_park_level_price',
            'forest_park_level_price',
            'wetland_level_price',
            'cultural_relic_level_price',
            'nature_reserve_level_price'
        ]
        
        if dry_run:
            self.stdout.write(self.style.WARNING('检查要迁移的表:'))
            for table in TABLES:
                self.stdout.write(f'  - {table}')
            self.stdout.write(self.style.SUCCESS('完成检查，使用 --no-dry-run 参数执行实际迁移'))
            return
        
        try:
            # 连接源数据库
            source_conn = MySQLdb.connect(
                host=SOURCE_DB['host'],
                user=SOURCE_DB['user'],
                passwd=SOURCE_DB['password'],
                db=SOURCE_DB['name'],
                port=SOURCE_DB['port']
            )
            self.stdout.write(self.style.SUCCESS('成功连接到源数据库'))
            
            # 连接目标数据库
            target_conn = MySQLdb.connect(
                host=TARGET_DB['host'],
                user=TARGET_DB['user'],
                passwd=TARGET_DB['password'],
                db=TARGET_DB['name'],
                port=TARGET_DB['port']
            )
            self.stdout.write(self.style.SUCCESS('成功连接到目标数据库'))
            
            # 迁移每个表
            success_count = 0
            for table in TABLES:
                if self.migrate_table(source_conn, target_conn, table):
                    success_count += 1
            
            # 关闭连接
            source_conn.close()
            target_conn.close()
            
            self.stdout.write(self.style.SUCCESS(f'数据迁移完成，成功迁移 {success_count}/{len(TABLES)} 个表'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'数据迁移过程中发生错误: {str(e)}'))
    
    def migrate_table(self, source_conn, target_conn, table_name):
        """迁移单个表的数据"""
        try:
            self.stdout.write(f"开始迁移表 {table_name}")
            
            # 获取表结构
            source_cursor = source_conn.cursor()
            source_cursor.execute(f"SHOW CREATE TABLE {table_name}")
            create_table_stmt = source_cursor.fetchone()[1]
            
            # 在目标数据库中创建表（如果不存在）
            target_cursor = target_conn.cursor()
            try:
                target_cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                target_cursor.execute(create_table_stmt)
                self.stdout.write(self.style.SUCCESS(f"在目标数据库中创建表 {table_name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"创建表失败: {str(e)}"))
                return False
            
            # 获取源数据库中的数据
            source_cursor.execute(f"SELECT * FROM {table_name}")
            rows = source_cursor.fetchall()
            if not rows:
                self.stdout.write(self.style.WARNING(f"表 {table_name} 中没有数据"))
                return True
            
            # 获取列名
            source_cursor.execute(f"DESCRIBE {table_name}")
            columns = [column[0] for column in source_cursor.fetchall()]
            
            # 在目标数据库中插入数据
            placeholders = ', '.join(['%s'] * len(columns))
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            target_cursor.executemany(insert_query, rows)
            target_conn.commit()
            
            self.stdout.write(self.style.SUCCESS(f"成功迁移表 {table_name}，共迁移 {len(rows)} 条数据"))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"迁移表 {table_name} 失败: {str(e)}"))
            return False 