import pytest
from unittest.mock import patch, Mock

from app.services.cache_service import CacheService


@pytest.mark.asyncio
async def test_cache_operations():
    mock_redis = Mock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True

    with patch('redis.asyncio.Redis') as mock_redis_class:
        mock_redis_class.return_value = mock_redis

        cache = CacheService(host='localhost', port=6379)
        await cache.set_cache('test_key', 'test_value')
        result = await cache.get_cache('test_key')
        assert result is None


def test_cache_key_generation():
    cache = CacheService()
    key = cache.generate_cache_key(
        "https://github.com/test/repo",
        "test task",
        "Junior"
    )
    assert isinstance(key, str)
