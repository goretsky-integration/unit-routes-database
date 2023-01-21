import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

import routers
from config import get_redis_settings
from db import mongo_db

app = FastAPI()
app.include_router(routers.auth.router)
app.include_router(routers.units.router)
app.include_router(routers.reports.router)
app.include_router(routers.accounts.router)
app.include_router(routers.report_types.router)
app.include_router(routers.ping.router)


@app.on_event('startup')
async def on_startup():
    redis = await aioredis.from_url(get_redis_settings().url, encoding='utf-8', decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache-database')


@app.on_event('shutdown')
async def on_shutdown():
    mongo_db.close_connection()
