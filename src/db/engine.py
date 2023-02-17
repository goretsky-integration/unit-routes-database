from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import postgresql_settings

__all__ = ('engine', 'session_factory')

engine = create_engine(postgresql_settings.url)
session_factory = sessionmaker(engine, expire_on_commit=False)
