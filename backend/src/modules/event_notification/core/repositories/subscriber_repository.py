from typing import Optional, List

from redis.asyncio import Redis

from src.core.logger import get_logger
from src.core.redis import get_redis
from src.general.repository.redis.redis_base_repository import BaseRedisRepository
from src.general.repository.redis.redis_query import RedisQuery

from .subscriber_mapper import SubscriberMapper
from ...models.subscriber_entity import (
    SubscriberFields,
    SubscriberEntity,
)

logger = get_logger(__name__)


class SubscriberRepository(
    BaseRedisRepository[SubscriberMapper, SubscriberFields, SubscriberEntity]
):
    SUBSCRIBER_PREFIX = "subscriber"

    def __init__(self, redis: Optional[Redis] = None, ttl: int = 3600):
        _mapper = SubscriberMapper()
        super().__init__(redis_client=redis or get_redis(), mapper=_mapper, ttl=ttl)

    async def add_subscriber(self, uuid: str) -> bool:
        entity = SubscriberEntity(uuid=uuid)
        await self.save(entity)
        return True

    async def remove_subscriber(self, uuid: str) -> bool:
        return await self.delete(uuid)

    async def get_subscribers(self) -> List[SubscriberEntity]:
        query = RedisQuery[SubscriberFields]()
        return await self.get_all(query)

    async def is_subscribed(self, uuid: str) -> bool:
        entity = await self.get_by_id(uuid)
        return entity is not None


def get_subscriber_repository(
    redis: Optional[Redis] = None,
) -> SubscriberRepository:
    return SubscriberRepository(redis)
