#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
从数据库中删除"东北"和"西北"区域数据
这是一个一次性脚本，用于清理数据库中的区域分类数据
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scenic_data_visualization.settings')
django.setup()

from scenic_data.models import ProvinceTraffic
from django.db import transaction
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def remove_region_data():
    """从ProvinceTraffic表中删除区域数据"""
    try:
        with transaction.atomic():
            # 查询要删除的记录
            regions_to_delete = ProvinceTraffic.objects.filter(province__in=["东北", "西北"])
            
            # 记录删除的数量
            count = regions_to_delete.count()
            
            if count > 0:
                # 执行删除
                regions_to_delete.delete()
                logger.info(f"成功删除了 {count} 条区域数据记录")
            else:
                logger.info("没有找到需要删除的区域数据记录")
                
            return count
    except Exception as e:
        logger.error(f"删除区域数据时出错: {e}")
        return 0

if __name__ == "__main__":
    logger.info("开始清理区域数据...")
    removed_count = remove_region_data()
    logger.info(f"区域数据清理完成，共删除了 {removed_count} 条记录") 