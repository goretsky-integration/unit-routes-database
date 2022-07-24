import redis.asyncio as async_redis
import redis.exceptions

from config import get_redis_settings
from utils import logger, exceptions

__all__ = (
    'close_connection',
    'ping',
)

connection = async_redis.from_url(get_redis_settings().url, decode_responses=True)


async def close_connection():
    await connection.close()
    logger.debug('Redis connection has been closed')


async def ping():
    try:
        await connection.ping()
    except redis.exceptions.ConnectionError as error:
        exceptions.DatabaseConnectionError(str(error))
    logger.debug('Redis connection has been established')
