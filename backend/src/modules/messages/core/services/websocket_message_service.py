import json
from typing import Any, Dict, Optional, Callable, Awaitable, List
import asyncio

from src.core.logger import get_logger
from src.modules.participants import PermissionService, get_permission_service

from ..repositories.websocket_message_repository import (
    WebSocketStateRepository,
    get_websocket_state_repository,
)

logger = get_logger(__name__)


class WebSocketMessageService:
    def __init__(
        self,
        state_repository: Optional[WebSocketStateRepository] = None,
        permission_service: Optional[PermissionService] = None,
        time_of_expire_per_seconds: Optional[int] = None,
    ):
        self.state_repo = state_repository or get_websocket_state_repository()
        self.time_of_expire_per_seconds = time_of_expire_per_seconds or 3600
        self.permission_service = permission_service or get_permission_service()

    async def _get_chat_participants(self, chat_uuid: str) -> List[str]:
        try:
            participants = await self.permission_service.get_by_resource(chat_uuid)
        except Exception as e:
            logger.error(f"Failed to get participants for chat {chat_uuid}: {e}")
            return []

        result: List[str] = []
        for p in participants or []:
            uuid = getattr(p, "user_uuid", None) or getattr(p, "uuid", None) or p
            if uuid:
                result.append(str(uuid))
        return result

    async def connect(self, user_uuid: str) -> bool:
        return await self.state_repo.set_user_online(user_uuid)

    async def disconnect(self, user_uuid: str) -> bool:
        return await self.state_repo.set_user_offline(user_uuid)

    async def notify_user(self, user_uuid: str, notification: Dict[str, Any]) -> None:
        await self.state_repo.publish_notification(user_uuid, notification)

    async def notify_chat_participants(
        self, chat_uuid: str, notification: Dict[str, Any]
    ) -> None:
        participants = await self._get_chat_participants(chat_uuid)
        for user_uuid in participants:
            await self.state_repo.publish_notification(user_uuid, notification)

    async def _parse_websocket_data(
        self, data: Any, user_uuid: str, send_message: Callable[[str], Awaitable[None]]
    ) -> None:
        if not data:
            return
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from client: {data}")
            return

        msg_type = parsed.get("type")

        if msg_type == "writing":
            chat_uuid = parsed.get("chat_uuid")
            if chat_uuid:
                await self.state_repo.add_active_chat(user_uuid, chat_uuid)
                await self.notify_chat_participants(
                    chat_uuid,
                    {"type": "typing", "data": {"user_uuid": user_uuid, "chat_uuid": chat_uuid}},
                )

        elif msg_type == "open_chat":
            chat_uuid = parsed.get("chat_uuid")
            if chat_uuid:
                await self.state_repo.add_active_chat(user_uuid, chat_uuid)
        elif msg_type == "close_chat":
            chat_uuid = parsed.get("chat_uuid")
            if chat_uuid:
                await self.state_repo.remove_active_chat(user_uuid, chat_uuid)
        elif msg_type == "ping":
            await send_message(json.dumps({"type": "pong"}))

    async def listen_messages(
        self,
        user_uuid: str,
        send_message: Callable[[str], Awaitable[None]],
        receive_message: Callable[[], Awaitable[str]],
    ) -> None:
        await self.connect(user_uuid)

        pubsub = self.state_repo.redis.pubsub()
        channel = await self.state_repo.get_notification_channel(user_uuid)
        await pubsub.subscribe(channel)

        redis_task: Optional[asyncio.Task] = None

        try:
            async def listen_redis():
                try:
                    async for message in pubsub.listen():
                        if message["type"] != "message":
                            continue
                        data = message["data"]
                        if isinstance(data, bytes):
                            data = data.decode()
                        await send_message(data)
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Redis listener error: {e}", exc_info=True)

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

            await pubsub.unsubscribe(channel)
            await pubsub.close()
            await self.disconnect(user_uuid)


_websocket_message_service: Optional[WebSocketMessageService] = None


def get_websocket_message_service() -> WebSocketMessageService:
    global _websocket_message_service
    if _websocket_message_service is None:
        _websocket_message_service = WebSocketMessageService()
    return _websocket_message_service
