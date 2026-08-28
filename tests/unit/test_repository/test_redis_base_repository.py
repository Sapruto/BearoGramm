import pytest
from unittest.mock import AsyncMock
from conftest import MockEntity, MockORM, MockFields


@pytest.mark.unit
class TestBaseRedisRepository:
    @pytest.mark.asyncio
    async def test_save(self, redis_repository, mock_redis):
        entity = MockEntity(id="1", name="test")
        result = await redis_repository.save(entity)
        assert result == entity
        mock_redis.hset.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id(self, redis_repository, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={b"id": b"1", b"name": b"test"})
        result = await redis_repository.get_by_id("1")
        assert result is not None
        assert result.id == "1"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, redis_repository, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={})
        result = await redis_repository.get_by_id("999")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_by_id(self, redis_repository, mock_redis):
        mock_redis.exists = AsyncMock(return_value=1)
        result = await redis_repository.delete_by_id("1")
        assert result is True
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_by_id_not_found(self, redis_repository, mock_redis):
        mock_redis.exists = AsyncMock(return_value=0)
        result = await redis_repository.delete_by_id("999")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists(self, redis_repository, mock_redis):
        mock_redis.exists = AsyncMock(return_value=1)
        result = await redis_repository.exists("1")
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_not_found(self, redis_repository, mock_redis):
        mock_redis.exists = AsyncMock(return_value=0)
        result = await redis_repository.exists("999")
        assert result is False

    @pytest.mark.asyncio
    async def test_batch_save(self, redis_repository, mock_redis):
        entities = [
            MockEntity(id="1", name="test1"),
            MockEntity(id="2", name="test2")
        ]
        result = await redis_repository.batch_save(entities)
        assert len(result) == 2
        assert mock_redis.hset.call_count == 2

    @pytest.mark.asyncio
    async def test_batch_delete(self, redis_repository, mock_redis):
        mock_redis.exists = AsyncMock(return_value=1)
        result = await redis_repository.batch_delete(["1", "2"])
        assert result == 2

    def test_enable_indexes(self, redis_repository):
        redis_repository.enable_indexes()
        assert redis_repository._index_enabled is True

    def test_disable_indexes(self, redis_repository):
        redis_repository.enable_indexes()
        redis_repository.disable_indexes()
        assert redis_repository._index_enabled is False
