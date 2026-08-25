from redis.asyncio import Redis
import json
from typing import Any, Optional
import asyncio
from fastapi import WebSocket

from src.modules.user import get_user_in_websocket
from src.core.redis import get_redis
from src.core.logger import get_logger

logger = get_logger(__name__)

class WebSocketMessageService:
    def __init__(self, redis: Optional[Redis] = None, time_of_expire_per_seconds: Optional[int] = None):
        self.redis = redis or get_redis()
        self.time_of_expire_per_seconds = time_of_expire_per_seconds or 3600

    async def _parse_websocket_data(self, data: Any, websocket: WebSocket, user_uuid: str):
        if data:
            try:
                parsed = json.loads(data)
                msg_type = parsed.get('type')

                if msg_type == 'writing':
                    msg_chat_uuid = parsed.get('chat_uuid')
                    if msg_chat_uuid:
                        notification = {
                            "type": "typing",
                            "data": {"user_uuid": user_uuid}
                        }
                        await self.notify_chat_participants(msg_chat_uuid, notification)
                elif msg_type == 'ping':
                    await websocket.send_text(json.dumps({'type': 'pong'}))

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from client: {data}")

    async def connect(self, user_uuid: str) -> bool:
        await self.redis.set(f"user:{user_uuid}:online", "1", ex=self.time_of_expire_per_seconds)
        return True

    async def disconnect(self, user_uuid: str) -> bool:
        await self.redis.delete(f"user:{user_uuid}:online")
        return True

    async def notify_user(self, user_uuid: str, notification: dict) -> None:
        await self.redis.publish(
            f"user:{user_uuid}:notifications",
            json.dumps(notification)
        )

    async def notify_chat_participants(self, chat_uuid: str, notification: dict) -> None:
        participants = await self.redis.smembers(f"chat:{chat_uuid}:users")

        for user_uuid in participants:
            user_uuid = user_uuid.decode() if isinstance(user_uuid, bytes) else user_uuid
            await self.notify_user(user_uuid, notification)

    async def listen_messages(self, websocket: WebSocket, user_uuid: str, token: str) -> None:
        try:
            user = await get_user_in_websocket(websocket, user_uuid, token)
            if not user:
                await websocket.close(code=4001, reason="Unauthorized")
                return
        except Exception as e:
            logger.error(f"WebSocket auth error: {e}")
            await websocket.close(code=4001, reason="Unauthorized")
            return

        await self.connect(user_uuid)
        await websocket.accept()

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f"user:{user_uuid}:notifications")

        redis_task = None
        try:
            async def listen_redis():
                try:
                    async for message in pubsub.listen():
                        if message['type'] == 'message':
                            await websocket.send_text(message['data'])
                except Exception as e:
                    logger.error(f"Redis listener error: {e}")

            redis_task = asyncio.create_task(listen_redis())

            while True:
                try:
                    data = await websocket.receive_text()
                    await self._parse_websocket_data(data, websocket, user_uuid)
                except Exception as e:
                    logger.error(f"WebSocket receive error: {e}")
                    break

        finally:
            if redis_task:
                redis_task.cancel()
            await pubsub.unsubscribe()
            await self.disconnect(user_uuid)

_websocket_message_service = WebSocketMessageService()

def get_websocket_message_service() -> WebSocketMessageService:
    global _websocket_message_service
    return _websocket_message_service
