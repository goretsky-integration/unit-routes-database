import redis
from django.conf import settings


def get_redis() -> redis.Redis:
    return redis.from_url(settings.REDIS_URL, decode_responses=True)
