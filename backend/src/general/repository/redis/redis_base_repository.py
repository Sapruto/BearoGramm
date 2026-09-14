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

    async def _to_redis(self, entity: EntityType) -> Dict[str, Any]:
        return await self._mapper.to_redis(entity)

    async def _to_entity(self, data: Dict[str, Any]) -> EntityType:
        return await self._mapper.to_entity(data)

    async def _to_redis_value(self, field: FieldsType, value: Any) -> tuple[str, Any]:
        return await self._mapper.to_redis_value(field, value)

    async def _to_entity_value(self, redis_field: str, value: Any) -> tuple[FieldsType, Any]:
        return await self._mapper.to_entity_value(redis_field, value)

    async def _to_redis_field(self, field: FieldsType) -> str:
        return await self._mapper.to_redis_field(field)

    async def _to_entity_field(self, redis_field: str) -> FieldsType:
        return await self._mapper.to_entity_field(redis_field)

    def _get_key(self, entity_id: Any) -> str:
        return self._mapper.get_key(entity_id)

    def _get_entity_id(self, entity: EntityType) -> Any:
        return self._mapper.get_id_from_entity(entity)

    async def _set_ttl(self, key: str, ttl: Optional[int] = None):
        if ttl:
            await self.redis.expire(key, ttl)
        elif self.default_ttl:
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
                return await self._to_entity(decoded_data)
            else:
                data = await self.redis.get(key)
                if not data:
                    return None
                if isinstance(data, bytes):
                    data = data.decode()
                parsed_data = json.loads(data)
                return await self._to_entity(parsed_data)

        except Exception as e:
            logger.error(f"Error getting entity by key {key}: {e}")
            return None

    async def _find_keys_by_query(self, query: RedisQuery[FieldsType]) -> List[str]:
        pattern = query.pattern or f"{self._mapper.key_prefix}:*"

        if query.filters and self._index_enabled and len(query.filters) == 1:
            field, value = next(iter(query.filters.items()))
            redis_field = await self._to_redis_field(field)
            index_key = f"{self._index_prefix}{redis_field}:{self._mapper.serialize_value(value)}"
            key = await self.redis.get(index_key)
            if key:
                return [key]
            return []

        keys: List[str] = []
        cursor = 0
        scan_count = query.scan_count or 100
        while True:
            cursor, batch = await self.redis.scan(cursor, match=pattern, count=scan_count)
            keys.extend(batch)
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

        data = await self._to_redis(entity)
        for redis_field, value in data.items():
            index_key = f"{self._index_prefix}{redis_field}:{self._mapper.serialize_value(value)}"
            await self.redis.delete(index_key)

    async def _rebuild_indexes_for_keys(self, keys: List[str]) -> None:
        if not keys:
            return

        pipe = self.redis.pipeline(transaction=False)
        for key in keys:
            if self._mapper.storage_type == "hash":
                await pipe.hgetall(key)
            else:
                await pipe.get(key)
        raw_results = await pipe.execute()

        pipe = self.redis.pipeline(transaction=False)
        for key, raw in zip(keys, raw_results):
            if not raw:
                continue
            if self._mapper.storage_type == "hash":
                data = raw
            else:
                data = json.loads(raw)
            for redis_field, value in data.items():
                idx_key = f"{self._index_prefix}{redis_field}:{self._mapper.serialize_value(value)}"
                await pipe.set(idx_key, key)
                if self.default_ttl:
                    await pipe.expire(idx_key, self.default_ttl)
        await pipe.execute()

    async def save(self, entity: EntityType) -> EntityType:
        entity_id = self._get_entity_id(entity)
        if entity_id is None:
            raise ValueError("Entity ID cannot be None")

        key = self._get_key(entity_id)
        new_data = await self._to_redis(entity)

        old_data: Optional[Dict[str, Any]] = None
        if self._index_enabled:
            old_entity = await self._get_by_key(key)
            if old_entity is not None:
                old_data = await self._to_redis(old_entity)

        pipe = self.redis.pipeline()
        if self._mapper.storage_type == "hash":
            await pipe.hset(key, mapping=new_data)
        else:
            await pipe.set(key, json.dumps(new_data, default=self._json_serializer))

        ttl = self.default_ttl
        if ttl:
            await pipe.expire(key, ttl)

        if self._index_enabled:
            if old_data:
                await pipe.delete(*[
                    f"{self._index_prefix}{f}:{self._mapper.serialize_value(v)}"
                    for f, v in old_data.items()
                ])
            for redis_field, value in new_data.items():
                idx_key = f"{self._index_prefix}{redis_field}:{self._mapper.serialize_value(value)}"
                await pipe.set(idx_key, key)
                if self.default_ttl:
                    await pipe.expire(idx_key, self.default_ttl)

        await pipe.execute()
        return entity

    async def delete(self, query: RedisQuery[FieldsType]) -> int:
        try:
            keys = await self._find_keys_by_query(query)
            if not keys:
                return 0

            if not self._index_enabled:
                return await self.redis.delete(*keys)

            pipe = self.redis.pipeline()
            for key in keys:
                entity = await self._get_by_key(key)
                if entity is None:
                    continue
                data = await self._to_redis(entity)
                for redis_field, value in data.items():
                    await pipe.delete(
                        f"{self._index_prefix}{redis_field}:{self._mapper.serialize_value(value)}"
                    )
            if keys:
                await pipe.delete(*keys)
            await pipe.execute()
            return len(keys)
        except Exception as e:
            logger.error(f"Error in delete in redis_repository: {e}")
            raise

    async def get_by_field(
        self, value: Any, field: FieldsType, select_field: Optional[FieldsType] = None
    ) -> Optional[EntityType]:
        try:
            if self._index_enabled:
                redis_field = await self._to_redis_field(field)
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
        if query.filters and self._index_enabled and len(query.filters) == 1:
            field, value = next(iter(query.filters.items()))
            redis_field = await self._to_redis_field(field)
            index_key = f"{self._index_prefix}{redis_field}:{self._mapper.serialize_value(value)}"
            return 1 if await self.redis.exists(index_key) else 0

        keys = await self._find_keys_by_query(query)
        if not query.filters:
            return len(keys)

        count = 0
        for key in keys:
            entity = await self._get_by_key(key)
            if entity and self._match_filters(entity, query.filters):
                count += 1
        return count

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
        if not entities:
            return []

        pipe = self.redis.pipeline(transaction=False)
        keys_to_invalidate: List[str] = []

        if self._index_enabled:
            for entity in entities:
                entity_id = self._get_entity_id(entity)
                if entity_id is None:
                    raise ValueError("Entity ID cannot be None")
                keys_to_invalidate.append(self._get_key(entity_id))

        for entity in entities:
            entity_id = self._get_entity_id(entity)
            if entity_id is None:
                raise ValueError("Entity ID cannot be None")
            key = self._get_key(entity_id)
            data = await self._to_redis(entity)

            if self._mapper.storage_type == "hash":
                await pipe.hset(key, mapping=data)
            else:
                await pipe.set(key, json.dumps(data, default=self._json_serializer))

            if self.default_ttl:
                await pipe.expire(key, self.default_ttl)

        await pipe.execute()

        if self._index_enabled:
            await self._rebuild_indexes_for_keys(keys_to_invalidate)

        return entities

    async def batch_delete(self, entity_ids: List[Any]) -> int:
        if not entity_ids:
            return 0

        keys = [self._get_key(eid) for eid in entity_ids]

        pipe = self.redis.pipeline(transaction=False)
        for key in keys:
            await pipe.exists(key)
        exists_flags = await pipe.execute()

        live_keys = [k for k, ok in zip(keys, exists_flags) if ok]
        if not live_keys:
            return 0

        pipe = self.redis.pipeline(transaction=False)
        if self._index_enabled:
            for key in live_keys:
                entity = await self._get_by_key(key)
                if entity is None:
                    continue
                data = await self._to_redis(entity)
                for redis_field, value in data.items():
                    await pipe.delete(
                        f"{self._index_prefix}{redis_field}:{self._mapper.serialize_value(value)}"
                    )
        await pipe.delete(*live_keys)
        await pipe.execute()
        return len(live_keys)

    def enable_indexes(self) -> "BaseRedisRepository":
        self._index_enabled = True
        return self

    def disable_indexes(self) -> "BaseRedisRepository":
        self._index_enabled = False
        return self
