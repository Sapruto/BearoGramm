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
    def __init__(self, redis_client: Redis, ttl: int = 3600):
        mapper = WebSocketStateMapper()
        super().__init__(redis_client=redis_client, mapper=mapper, ttl=ttl)
        self.enable_indexes()

        self.USER_ONLINE_PREFIX = "user:online"
        self.CHAT_USERS_PREFIX = "chat:users"
        self.USER_NOTIFICATIONS_PREFIX = "user:notifications"

    async def set_user_online(self, user_uuid: str) -> bool:
        entity = WebSocketStateEntity(
            user_uuid=user_uuid, online=True, last_activity=True
        )
        await self.save(entity)

        key = f"{self.USER_ONLINE_PREFIX}:{user_uuid}"
        await self.redis.setex(key, self.ttl, "1")

        return True

    async def set_user_offline(self, user_uuid: str) -> bool:
        entity = await self.get_by_id(user_uuid)
        if entity:
            entity.online = False
            await self.save(entity)

        key = f"{self.USER_ONLINE_PREFIX}:{user_uuid}"
        await self.redis.delete(key)

        return True

    async def is_user_online(self, user_uuid: str) -> bool:
        key = f"{self.USER_ONLINE_PREFIX}:{user_uuid}"
        return await self.redis.exists(key) > 0

    async def get_online_users(self) -> List[WebSocketStateEntity]:
        query = RedisQuery[WebSocketStateFields]()
        query.add_filter(WebSocketStateFields.ONLINE, True)
        return await self.get_all(query)

    async def add_user_to_chat(self, chat_uuid: str, user_uuid: str) -> None:
        key = f"{self.CHAT_USERS_PREFIX}:{chat_uuid}"
        await self.redis.sadd(key, user_uuid)
        await self.redis.expire(key, self.ttl)

    async def remove_user_from_chat(self, chat_uuid: str, user_uuid: str) -> None:
        key = f"{self.CHAT_USERS_PREFIX}:{chat_uuid}"
        await self.redis.srem(key, user_uuid)

    async def get_chat_participants(self, chat_uuid: str) -> Set[str]:
        key = f"{self.CHAT_USERS_PREFIX}:{chat_uuid}"
        members = await self.redis.smembers(key)
        return {m.decode() if isinstance(m, bytes) else m for m in members}

    async def clear_chat_participants(self, chat_uuid: str) -> None:
        key = f"{self.CHAT_USERS_PREFIX}:{chat_uuid}"
        await self.redis.delete(key)

    async def publish_notification(
        self, user_uuid: str, notification: Dict[str, Any]
    ) -> None:
        channel = f"{self.USER_NOTIFICATIONS_PREFIX}:{user_uuid}"
        await self.redis.publish(channel, json.dumps(notification))

    async def publish_to_chat(
        self, chat_uuid: str, notification: Dict[str, Any]
    ) -> None:
        participants = await self.get_chat_participants(chat_uuid)
        for user_uuid in participants:
            await self.publish_notification(user_uuid, notification)

    async def get_notification_channel(self, user_uuid: str) -> str:
        return f"{self.USER_NOTIFICATIONS_PREFIX}:{user_uuid}"

    async def ping(self) -> bool:
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False


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
