import hashlib
import json
import logging
from typing import Optional, Any

import redis.asyncio as redis
from fastapi import HTTPException


class CacheService:
    logger = logging.getLogger('cache_service')

    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_timeout=5
            )
            self.logger.info("Redis connection established")
        except redis.ConnectionError as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise HTTPException(status_code=500, detail="Cache service unavailable")

    async def get_cache(self, key: str) -> Optional[Any]:
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting cache: {e}")
            return None

    async def set_cache(self, key: str, value: Any, expiry: int = 3600) -> bool:
        try:
            serialized_value = json.dumps(value)
            await self.redis.setex(key, expiry, serialized_value)
            return True
        except Exception as e:
            self.logger.error(f"Error setting cache: {e}")
            return False

    async def delete_cache(self, key: str) -> bool:
        try:
            return bool(await self.redis.delete(key))
        except Exception as e:
            self.logger.error(f"Error deleting cache: {e}")
            return False

    @staticmethod
    def generate_cache_key(github_url: str, task_description: str, level: str) -> str:
        try:
            key_string = f"{github_url}_{task_description}_{level}"
            return hashlib.md5(key_string.encode()).hexdigest()
        except Exception as e:
            CacheService.logger.error(f"Error generating cache key: {e}")
            raise HTTPException(status_code=500, detail="Error generating cache key")

    async def health_check(self) -> bool:
        try:
            return await self.redis.ping()
        except Exception as e:
            self.logger.error(f"Redis health check failed: {e}")
            return False

cache_service = CacheService()
