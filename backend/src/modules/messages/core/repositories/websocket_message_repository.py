from typing import Optional, Set, List, Dict, Any
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
    USER_ACTIVE_CHATS_PREFIX = "user:active_chats"
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

    async def add_active_chat(self, user_uuid: str, chat_uuid: str) -> None:
        key = f"{self.USER_ACTIVE_CHATS_PREFIX}:{user_uuid}"
        await self.redis.sadd(key, chat_uuid)
        await self.redis.expire(key, self.default_ttl)

    async def remove_active_chat(self, user_uuid: str, chat_uuid: str) -> None:
        key = f"{self.USER_ACTIVE_CHATS_PREFIX}:{user_uuid}"
        await self.redis.srem(key, chat_uuid)

    async def get_active_chats(self, user_uuid: str) -> Set[str]:
        key = f"{self.USER_ACTIVE_CHATS_PREFIX}:{user_uuid}"
        members = await self.redis.smembers(key)
        return {m.decode() if isinstance(m, bytes) else m for m in members}

    async def clear_active_chats(self, user_uuid: str) -> None:
        await self.redis.delete(f"{self.USER_ACTIVE_CHATS_PREFIX}:{user_uuid}")

    async def publish_notification(
        self, user_uuid: str, notification: Dict[str, Any]
    ) -> None:
        channel = f"{self.USER_NOTIFICATIONS_PREFIX}:{user_uuid}"
        subscribers = await self.redis.publish(
            channel, json.dumps(notification, ensure_ascii=False)
        )
        logger.debug(
            f"PUBLISH → {channel} | subscribers={subscribers} | "
            f"type={notification.get('type')}"
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
