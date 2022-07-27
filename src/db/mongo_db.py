from motor.motor_asyncio import AsyncIOMotorClient

from config import get_mongo_db_settings
from utils import logger

__all__ = (
    'units',
    'reports',
    'accounts',
    'report_types',
    'statistics_report_types',
    'cookies',
    'tokens',
    'close_connection',
)

client = AsyncIOMotorClient(get_mongo_db_settings().url)
db = client.dodo
units = db.units
reports = db.reports
accounts = db.accounts
report_types = db.report_types
statistics_report_types = db.statistics_report_types
cookies = db.cookies
tokens = db.tokens


def close_connection():
    client.close()
    logger.debug('Mongodb connection has been closed')
