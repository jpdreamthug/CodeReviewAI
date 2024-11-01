import redis.asyncio as redis
import json
import hashlib
import logging
from typing import Optional, Any
from redis.exceptions import ConnectionError, RedisError
from app.core.config import settings


class CacheService:
    logger = logging.getLogger("cache_service")

    def __init__(self):
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True,
                socket_timeout=5,
            )
        except ConnectionError as e:
            self.logger.error(f"Redis connection failed: {e}")
            self.redis = None

    async def get_cache(self, key: str) -> Optional[Any]:
        if not self.redis:
            return None

        try:
            cached_data = await self.redis.get(key)
            return json.loads(cached_data) if cached_data else None
        except RedisError as e:
            self.logger.error(f"Redis get error: {e}")
            return None

    async def set_cache(self, key: str, value: Any, expiry: int = 3600) -> bool:
        if not self.redis:
            return False

        try:
            await self.redis.setex(key, expiry, json.dumps(value))
            return True
        except RedisError as e:
            self.logger.error(f"Redis set error: {e}")
            return False

    @staticmethod
    def generate_cache_key(github_url: str, task_description: str, level: str) -> str:
        key_string = f"{github_url}_{task_description}_{level}"
        return hashlib.md5(key_string.encode()).hexdigest()


cache_service = CacheService()
