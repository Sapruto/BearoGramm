from redis.asyncio import Redis
from redis.asyncio.client import PubSub
from typing import Optional
import json

from src.core.redis import get_redis
from src.core.logger import get_logger
from src.general.repository.redis.redis_base_repository import BaseRedisRepository
from src.general.repository.exception import NotConvertableError

from .mappers.calls_state_mapper import CallsStateMapper
from ...models.entities.call_state_entity import CallStateFields, CallStateEntity

logger = get_logger(__name__)


class CallsStateRepository(
    BaseRedisRepository[CallsStateMapper, CallStateFields, CallStateEntity]
):
    def __init__(self, redis_client: Optional[Redis] = None):
        mapper = CallsStateMapper()
        super().__init__(redis_client or get_redis(), mapper, ttl=86400)
        self.enable_indexes()

    async def save(self, entity: CallStateEntity) -> CallStateEntity:
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

            await self._set_ttl(key, entity.ttl)

            if self._index_enabled:
                await self._update_indexes(key, data)

            return entity

        except NotConvertableError as e:
            logger.error(f"Conversion error in save: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in save: {e}")
            raise

    async def notify_user(self, user_uuid: str, data: dict) -> None:
        await self.redis.publish(f"user:{user_uuid}:notifications", json.dumps(data))

    async def pubsub(self) -> PubSub:
        return self.redis.pubsub()


def get_calls_state_repository() -> CallsStateRepository:
    return CallsStateRepository()
