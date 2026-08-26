import json
from typing import Any, Dict, Optional, Callable, Awaitable
import asyncio

from src.core.logger import get_logger

from ..repositories.websocket_message_repository import WebSocketStateRepository, get_websocket_state_repository

logger = get_logger(__name__)

class WebSocketMessageService:
    def __init__(self, state_repository: Optional[WebSocketStateRepository] = None, time_of_expire_per_seconds: Optional[int] = None):
        self.state_repo = state_repository or get_websocket_state_repository()
        self.time_of_expire_per_seconds = time_of_expire_per_seconds or 3600

    async def _parse_websocket_data(self, data: Any, user_uuid: str, send_message: Callable[[str], Awaitable[None]]) -> None:
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
                    await send_message(json.dumps({'type': 'pong'}))

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from client: {data}")

    async def connect(self, user_uuid: str) -> bool:
        return await self.state_repo.set_user_online(user_uuid)

    async def disconnect(self, user_uuid: str) -> bool:
        return await self.state_repo.set_user_offline(user_uuid)

    async def notify_user(self, user_uuid: str, notification: Dict[str, Any]) -> None:
        await self.state_repo.publish_notification(user_uuid, notification)

    async def notify_chat_participants(self, chat_uuid: str, notification: Dict[str, Any]) -> None:
        await self.state_repo.publish_to_chat(chat_uuid, notification)

    async def listen_messages(self, user_uuid: str, send_message: Callable[[str], Awaitable[None]], receive_message: Callable[[], Awaitable[str]]) -> None:
        await self.connect(user_uuid)

        pubsub = self.state_repo.redis.pubsub()
        notification_channel = await self.state_repo.get_notification_channel(user_uuid)
        await pubsub.subscribe(notification_channel)

        redis_task = None

        try:
            async def listen_redis():
                try:
                    async for message in pubsub.listen():
                        if message['type'] == 'message':
                            data = message['data']
                            if isinstance(data, bytes):
                                data = data.decode()
                            await send_message(data)
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Redis listener error: {e}")

            redis_task = asyncio.create_task(listen_redis())

            while True:
                try:
                    data = await receive_message()
                    await self._parse_websocket_data(data, user_uuid, send_message)
                except Exception as e:
                    logger.error(f"WebSocket receive error: {e}")
                    break

        finally:
            if redis_task and not redis_task.done():
                redis_task.cancel()
                try:
                    await redis_task
                except asyncio.CancelledError:
                    pass

            await pubsub.unsubscribe()
            await self.disconnect(user_uuid)

_websocket_message_service = WebSocketMessageService()

def get_websocket_message_service() -> WebSocketMessageService:
    global _websocket_message_service
    return _websocket_message_service
