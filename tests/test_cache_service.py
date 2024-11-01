import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_cache_operations(mock_settings):
    with patch('redis.asyncio.Redis') as mock_redis_class:
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis_class.return_value = mock_redis

        from app.services.cache_service import CacheService
        cache_service = CacheService()

        success = await cache_service.set_cache('test_key', 'test_value')
        assert success is True

        result = await cache_service.get_cache('test_key')
        assert result is None

        mock_redis.setex.assert_called_once()
        mock_redis.get.assert_called_once_with('test_key')


def test_cache_key_generation(mock_settings):
    from app.services.cache_service import CacheService
    cache = CacheService()

    key = cache.generate_cache_key(
        "https://github.com/test/repo",
        "test task",
        "Junior"
    )
    assert isinstance(key, str)
    assert len(key) == 32
