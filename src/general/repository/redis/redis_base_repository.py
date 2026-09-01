from typing import Generic, Optional, Any, List, Dict, TypeVar
import json
from datetime import datetime
from redis.asyncio import Redis

from src.core.logger import get_logger
from src.general.repository.exception import NotConvertableError
from src.general.repository.redis.redis_base_mapper import BaseRedisMapper
from src.general.repository.redis.redis_query import RedisQuery
from src.general.types_var import Entity as EntityType, Fields as FieldsType

from ..interfaces.base_repository_interface import BaseRepositoryInterface

logger = get_logger(__name__)

Mapper = TypeVar("Mapper", bound=BaseRedisMapper)


class BaseRedisRepository(
    Generic[Mapper, FieldsType, EntityType],
    BaseRepositoryInterface[RedisQuery[FieldsType], FieldsType, EntityType],
):
    def __init__(self, redis_client: Redis, mapper: Mapper, ttl: Optional[int] = None):
        self.redis = redis_client
        self._mapper = mapper
        self.default_ttl = ttl

        self._index_enabled = False
        self._index_prefix = f"idx:{mapper.key_prefix}:"

    def _to_redis(self, entity: EntityType) -> Dict[str, Any]:
        return self._mapper.to_redis(entity)

    def _to_entity(self, data: Dict[str, Any]) -> EntityType:
        return self._mapper.to_entity(data)

    def _to_redis_value(self, field: FieldsType, value: Any) -> tuple[str, Any]:
        return self._mapper.to_redis_value(field, value)

    def _to_entity_value(self, redis_field: str, value: Any) -> tuple[FieldsType, Any]:
        return self._mapper.to_entity_value(redis_field, value)

    def _to_redis_field(self, field: FieldsType) -> str:
        return self._mapper.to_redis_field(field)

    def _to_entity_field(self, redis_field: str) -> FieldsType:
        return self._mapper.to_entity_field(redis_field)

    def _get_key(self, entity_id: Any) -> str:
        return self._mapper.get_key(entity_id)

    def _get_entity_id(self, entity: EntityType) -> Any:
        return self._mapper.get_id_from_entity(entity)

    async def _set_ttl(self, key: str, ttl: int):
        if ttl:
            await self.redis.expire(key, ttl)
        if self.default_ttl:
            await self.redis.expire(key, self.default_ttl)

    def _json_serializer(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        raise TypeError(f"Type {type(obj)} not serializable")

    async def _get_by_key(self, key: str) -> Optional[EntityType]:
        try:
            storage_type = self._mapper.storage_type

            if storage_type == "hash":
                data = await self.redis.hgetall(key)
                if not data:
                    return None
                decoded_data = {}
                for k, v in data.items():
                    decoded_data[k.decode() if isinstance(k, bytes) else k] = (
                        v.decode() if isinstance(v, bytes) else v
                    )
                return self._to_entity(decoded_data)
            else:
                data = await self.redis.get(key)
                if not data:
                    return None
                if isinstance(data, bytes):
                    data = data.decode()
                parsed_data = json.loads(data)
                return self._to_entity(parsed_data)

        except Exception as e:
            logger.error(f"Error getting entity by key {key}: {e}")
            return None

    async def _find_keys_by_query(self, query: RedisQuery[FieldsType]) -> List[str]:
        if query.pattern:
            pattern = query.pattern
        else:
            pattern = f"{self._mapper.key_prefix}:*"

        if query.filters and self._index_enabled and len(query.filters) == 1:
            field, value = next(iter(query.filters.items()))
            redis_field = self._to_redis_field(field)
            index_key = f"{self._index_prefix}{redis_field}:{self._mapper.serialize_value(value)}"
            key = await self.redis.get(index_key)
            if key:
                return [key.decode() if isinstance(key, bytes) else key]

        keys = []
        cursor = 0
        scan_count = query.scan_count or 100

        while True:
            cursor, scan_keys = await self.redis.scan(
                cursor, match=pattern, count=scan_count
            )
            for key in scan_keys:
                if isinstance(key, bytes):
                    key = key.decode()
                keys.append(key)
            if cursor == 0:
                break

        return keys

    def _match_filters(
        self, entity: EntityType, filters: Dict[FieldsType, Any]
    ) -> bool:
        if not filters:
            return True

        for field, value in filters.items():
            entity_value = getattr(entity, field, None)
            if entity_value != value:
                return False
        return True

    def _apply_sorting(
        self, entities: List[EntityType], order_by: List[tuple]
    ) -> List[EntityType]:
        if not order_by:
            return entities

        def sort_key(entity):
            key_tuple = []
            for field, direction in order_by:
                value = getattr(entity, field, None)
                if isinstance(value, (int, float)):
                    key_tuple.append(value if direction == "asc" else -value)
                else:
                    key_tuple.append(value)
            return tuple(key_tuple)

        return sorted(entities, key=sort_key)

    async def _update_indexes(self, key: str, data: Dict[str, Any]):
        for redis_field, value in data.items():
            index_key = f"{self._index_prefix}{redis_field}:{self._mapper.serialize_value(value)}"
            await self.redis.set(index_key, key)
            if self.default_ttl:
                await self.redis.expire(index_key, self.default_ttl)

    async def _remove_indexes(self, key: str):
        entity = await self._get_by_key(key)
        if not entity:
            return

        data = self._to_redis(entity)
        for redis_field, value in data.items():
            index_key = f"{self._index_prefix}{redis_field}:{self._mapper.serialize_value(value)}"
            await self.redis.delete(index_key)

    async def save(self, entity: EntityType) -> EntityType:
        try:
            entity_id = self._get_entity_id(entity)
            if entity_id is None:
                raise ValueError("Entity ID cannot be None")

            key = self._get_key(entity_id)
            data = self._to_redis(entity)

            storage_type = self._mapper.storage_type

            if storage_type == "hash":
                await self.redis.hset(key, mapping=data)
            else:
                await self.redis.set(
                    key, json.dumps(data, default=self._json_serializer)
                )

            await self._set_ttl(key)

            if self._index_enabled:
                await self._update_indexes(key, data)

            return entity

        except NotConvertableError as e:
            logger.error(f"Conversion error in save: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in save: {e}")
            raise

    async def delete(self, query: RedisQuery[FieldsType]) -> int:
        try:
            keys = await self._find_keys_by_query(query)
            if not keys:
                return 0

            if self._index_enabled:
                for key in keys:
                    await self._remove_indexes(key)

            if len(keys) == 1:
                await self.redis.delete(keys[0])
                return 1
            else:
                return await self.redis.delete(*keys)

        except NotConvertableError as e:
            logger.error(f"Conversion error in delete: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in delete: {e}")
            raise

    async def get_by_field(
        self, value: Any, field: FieldsType, select_field: Optional[FieldsType] = None
    ) -> Optional[EntityType]:
        try:
            if self._index_enabled:
                redis_field = self._to_redis_field(field)
                index_key = f"{self._index_prefix}{redis_field}:{self._mapper.serialize_value(value)}"
                key = await self.redis.get(index_key)
                if key:
                    key_str = key.decode() if isinstance(key, bytes) else key
                    entity = await self._get_by_key(key_str)
                    if entity and select_field:
                        return getattr(entity, select_field)
                    return entity

            pattern = f"{self._mapper.key_prefix}:*"
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                for key in keys:
                    key_str = key.decode() if isinstance(key, bytes) else key
                    entity = await self._get_by_key(key_str)
                    if entity and getattr(entity, field) == value:
                        if select_field:
                            return getattr(entity, select_field)
                        return entity
                if cursor == 0:
                    break

            return None

        except NotConvertableError as e:
            logger.error(f"Conversion error in get_by_field: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_by_field: {e}")
            raise

    async def get(self, query: RedisQuery[FieldsType]) -> Optional[EntityType]:
        try:
            original_limit = query.limit
            query.limit = 1

            results = await self.get_all(query)

            query.limit = original_limit

            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error in get: {e}")
            raise

    async def get_all(self, query: RedisQuery[FieldsType]) -> List[EntityType]:
        try:
            keys = await self._find_keys_by_query(query)

            if query.offset:
                keys = keys[query.offset :]
            if query.limit:
                keys = keys[: query.limit]

            entities = []
            for key in keys:
                entity = await self._get_by_key(key)
                if entity and self._match_filters(entity, query.filters or {}):
                    entities.append(entity)

            if query.order_by:
                entities = self._apply_sorting(entities, query.order_by)

            return entities

        except Exception as e:
            logger.error(f"Error in get_all: {e}")
            raise

    async def count(self, query: RedisQuery[FieldsType]) -> int:
        try:
            keys = await self._find_keys_by_query(query)

            if query.filters:
                count = 0
                for key in keys:
                    entity = await self._get_by_key(key)
                    if entity and self._match_filters(entity, query.filters):
                        count += 1
                return count

            return len(keys)

        except Exception as e:
            logger.error(f"Error in count: {e}")
            raise

    async def get_by_id(self, entity_id: Any) -> Optional[EntityType]:
        key = self._get_key(entity_id)
        return await self._get_by_key(key)

    async def delete_by_id(self, entity_id: Any) -> bool:
        key = self._get_key(entity_id)
        if await self.redis.exists(key):
            if self._index_enabled:
                await self._remove_indexes(key)
            await self.redis.delete(key)
            return True
        return False

    async def exists(self, entity_id: Any) -> bool:
        key = self._get_key(entity_id)
        return await self.redis.exists(key) > 0

    async def batch_save(self, entities: List[EntityType]) -> List[EntityType]:
        saved = []
        for entity in entities:
            saved_entity = await self.save(entity)
            saved.append(saved_entity)
        return saved

    async def batch_delete(self, entity_ids: List[Any]) -> int:
        deleted = 0
        for entity_id in entity_ids:
            if await self.delete_by_id(entity_id):
                deleted += 1
        return deleted

    def enable_indexes(self) -> "BaseRedisRepository":
        self._index_enabled = True
        return self

    def disable_indexes(self) -> "BaseRedisRepository":
        self._index_enabled = False
        return self
