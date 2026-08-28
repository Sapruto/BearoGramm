import pytest
from unittest.mock import AsyncMock, MagicMock
from redis.asyncio import Redis
from pydantic import BaseModel
from enum import Enum

from src.general.repository.redis.redis_base_repository import BaseRedisRepository
from src.general.repository.redis.redis_base_mapper import BaseRedisMapper
from src.general.repository.sql.sql_base_repository import BaseRepository
from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.general.db.base_manager import BaseManager


class MockFields(str, Enum):
    ID = "id"
    NAME = "name"


class MockEntity(BaseModel):
    id: str
    name: str


class MockORM:
    def __init__(self, id: str = None, name: str = None):
        self.id = id
        self.name = name


class MockRedisMapper(BaseRedisMapper[MockEntity, MockFields]):
    key_prefix = "test"
    storage_type = "hash"

    field_mapping = {
        MockFields.ID: "id",
        MockFields.NAME: "name",
    }

    def to_redis(self, entity: MockEntity) -> dict:
        return {"id": entity.id, "name": entity.name}

    def to_entity(self, data: dict) -> MockEntity:
        return MockEntity(id=data.get("id", ""), name=data.get("name", ""))

    def to_redis_value(self, field, value):
        return self.to_redis_field(field), str(value)

    def to_entity_value(self, redis_field, value):
        return self.to_entity_field(redis_field), value

    def to_redis_field(self, field):
        return self.field_mapping.get(field, str(field))

    def to_entity_field(self, redis_field):
        return self.reverse_field_mapping.get(redis_field, MockFields.ID)

    def get_id_field(self):
        return MockFields.ID

    def get_id_from_entity(self, entity):
        return entity.id


class MockSqlMapper(BaseMapper[MockEntity, MockORM, MockFields]):
    field_mapping = {
        MockFields.ID: "id",
        MockFields.NAME: "name",
    }

    def to_orm(self, entity):
        return MockORM(id=entity.id, name=entity.name)

    def to_entity(self, orm):
        return MockEntity(id=orm.id, name=orm.name)

    def to_orm_value(self, field, value):
        return self.to_orm_field(field), value

    def to_entity_value(self, field, value):
        return self.to_entity_field(field), value

    def to_orm_field(self, field):
        return self.field_mapping.get(field)

    def to_entity_field(self, field):
        return self.reverse_field_mapping.get(field)


class MockManager(BaseManager[MockORM]):
    def __init__(self):
        self.model = MockORM
        self.create = AsyncMock()
        self.delete = AsyncMock()
        self.get_by_field = AsyncMock()
        self.get_all = AsyncMock()
        self.count = AsyncMock()
        self.update = AsyncMock()

    def identifier_field(self):
        return "id"


@pytest.fixture
def mock_redis():
    redis = MagicMock(spec=Redis)
    redis.hset = AsyncMock(return_value=1)
    redis.hgetall = AsyncMock()
    redis.delete = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    redis.scan = AsyncMock(return_value=(0, []))
    redis.exists = AsyncMock(return_value=1)
    redis.set = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    return redis


@pytest.fixture
def redis_repository(mock_redis):
    repo = BaseRedisRepository(
        redis_client=mock_redis,
        mapper=MockRedisMapper(),
        ttl=3600
    )
    repo._index_enabled = False
    repo._set_ttl = AsyncMock()
    return repo


@pytest.fixture
def manager():
    return MockManager()


@pytest.fixture
def sql_repository(manager):
    return BaseRepository(manager=manager, mapper=MockSqlMapper())