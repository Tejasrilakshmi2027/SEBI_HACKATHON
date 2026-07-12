import redis.asyncio as redis
from app.core.config import settings

redis_client: redis.Redis = None


async def connect_to_redis():
    global redis_client
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )


async def close_redis_connection():
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis():
    return redis_client
