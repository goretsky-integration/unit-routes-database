from motor.motor_asyncio import AsyncIOMotorClient

from config import get_mongo_db_settings
from utils import logger

__all__ = (
    'units',
    'reports',
    'accounts',
    'close_connection',
)


client = AsyncIOMotorClient(get_mongo_db_settings().url)
db = client.dodo
units = db.units
reports = db.reports
accounts = db.accounts


async def close_connection():
    await client.close()
    logger.debug('Mongodb connection has been closed')
