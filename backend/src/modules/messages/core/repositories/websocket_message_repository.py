from typing import Optional, List, Dict, Any
from redis.asyncio import Redis
import json

from src.core.logger import get_logger
from src.general.repository.redis.redis_base_repository import BaseRedisRepository
from src.general.repository.redis.redis_query import RedisQuery

from .mappers.websocket_state_mapper import WebSocketStateMapper
from ...models.entities.websocket_state_entity import (
    WebSocketStateFields,
    WebSocketStateEntity,
)


logger = get_logger(__name__)


class WebSocketStateRepository(
    BaseRedisRepository[
        WebSocketStateMapper, WebSocketStateFields, WebSocketStateEntity
    ]
):
    USER_ONLINE_PREFIX = "user:online"
    USER_NOTIFICATIONS_PREFIX = "user:notifications"

    def __init__(self, redis_client: Redis, ttl: int = 3600):
        mapper = WebSocketStateMapper()
        super().__init__(redis_client=redis_client, mapper=mapper, ttl=ttl)

    async def set_user_online(self, user_uuid: str) -> bool:
        entity = WebSocketStateEntity(user_uuid=user_uuid, online=True)
        await self.save(entity)
        return True

    async def set_user_offline(self, user_uuid: str) -> bool:
        entity = await self.get_by_id(user_uuid)
        if entity:
            entity.online = False
            await self.save(entity)
        return True

    async def is_user_online(self, user_uuid: str) -> bool:
        entity = await self.get_by_id(user_uuid)
        return bool(entity and entity.online)

    async def get_online_users(self) -> List[WebSocketStateEntity]:
        query = RedisQuery[WebSocketStateFields]()
        query.add_filter(WebSocketStateFields.ONLINE, True)
        return await self.get_all(query)

    async def publish_notification(
        self, user_uuid: str, notification: Dict[str, Any]
    ) -> None:
        channel = f"{self.USER_NOTIFICATIONS_PREFIX}:{user_uuid}"
        await self.redis.publish(
            channel, json.dumps(notification, ensure_ascii=False)
        )

    async def get_notification_channel(self, user_uuid: str) -> str:
        return f"{self.USER_NOTIFICATIONS_PREFIX}:{user_uuid}"


_websocket_state_repository: Optional[WebSocketStateRepository] = None


def get_websocket_state_repository(
    redis: Optional[Redis] = None,
) -> WebSocketStateRepository:
    global _websocket_state_repository
    if _websocket_state_repository is None:
        from src.core.redis import get_redis

        redis_client = redis or get_redis()
        _websocket_state_repository = WebSocketStateRepository(redis_client)
    return _websocket_state_repository
