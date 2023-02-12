import pathlib

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

__all__ = (
    'ROOT_PATH',
    'LOG_FILE_PATH',
    'PostgresqlSettings',
    'AppSettings',
    'app_settings',
    'postgresql_settings',
)

ROOT_PATH = pathlib.Path(__file__).parent.parent
LOG_FILE_PATH = ROOT_PATH / 'logs.log'

load_dotenv()


class AppSettings(BaseSettings):
    host: str = Field(env='APP_HOST')
    port: int = Field(env='APP_PORT')
    debug: bool = Field(env='DEBUG')


class PostgresqlSettings(BaseSettings):
    url: str = Field(env='DATABASE_URL')


app_settings = AppSettings()
postgresql_settings = PostgresqlSettings()
