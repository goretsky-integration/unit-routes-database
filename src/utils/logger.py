from loguru import logger

from config import LOG_FILE_PATH

__all__ = (
    'logger',
)

logger.add(LOG_FILE_PATH, level='DEBUG', retention='3 days')
