import redis
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True  # 自动将字节解码为字符串
)

# 创建Redis连接
redis_client = redis.Redis(connection_pool=redis_pool)

# 测试Redis连接
try:
    redis_client.ping()
    logger.info("Redis连接成功")
except redis.ConnectionError as e:
    logger.error(f"Redis连接失败: {str(e)}")
except Exception as e:
    logger.error(f"Redis操作异常: {str(e)}")