from redis.asyncio import Redis
import json
from typing import Optional

from src.core.redis import get_redis

class WebSocketMessageService:
    def __init__(self, redis: Optional[Redis] = None, time_of_expire_per_seconds: Optional[int] = None):
        self.redis = redis or get_redis()
        self.time_of_expire_per_seconds = time_of_expire_per_seconds or 3600

    async def connect(self, user_uuid: str, chat_uuid: str) -> bool:
        await self.redis.hset(f"user:{user_uuid}", "chat", chat_uuid)
        await self.redis.sadd(f"chat:{chat_uuid}:users", user_uuid)
        await self.redis.expire(f"user:{user_uuid}", self.time_of_expire_per_seconds)
        return True

    async def disconnect(self, user_uuid: str) -> bool:
        user_data = await self.redis.hgetall(f"user:{user_uuid}")
        chat_uuid = user_data.get("chat")

        if chat_uuid:
            await self.redis.srem(f"chat:{chat_uuid}:users", user_uuid)

        await self.redis.delete(f"user:{user_uuid}")
        return True

    async def notify_about_message(self, chat_uuid: str, message: dict) -> None:
        await self.redis.publish(
            f"chat:{chat_uuid}:messages",
            json.dumps(message)
        )

    async def notify_about_writing(self, user_uuid: str, chat_uuid: str) -> None:
        await self.redis.publish(
            f"chat:{chat_uuid}:typing",
            json.dumps({"user_uuid": user_uuid})
        )

_websocket_message_service = WebSocketMessageService()

def get_websocket_message_service() -> WebSocketMessageService:
    global _websocket_message_service
    return _websocket_message_service
