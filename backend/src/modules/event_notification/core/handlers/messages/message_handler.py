from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Optional

from src.core.logger import get_logger
from ...services.event_notification_service import get_notification_event_service, EventNotificationService

logger = get_logger(__name__)


class EventType(str, Enum):
    TYPING = "typing"
    MESSAGE_CREATED = "message_created"
    USER_ONLINE = "user_online"

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)


class MessageHandler:
    def __init__(self, notification_service: Optional[EventNotificationService] = None):
        self._notification_service = notification_service or get_notification_event_service()

    async def on_typing(self, payload: Dict[str, Any]) -> Optional[str]:
        user_uuid = payload.get("user_uuid")
        chat_uuid = payload.get("chat_uuid")
        if not user_uuid or not chat_uuid:
            return None

        await self._notification_service.notify_user(
            user_uuid,
            {
                "type": EventType.TYPING,
                "data": {"user_uuid": user_uuid, "chat_uuid": chat_uuid},
            },
        )
        return "success"

    async def on_message_created(self, payload: Dict[str, Any]) -> Optional[str]:
        chat_uuid = payload.get("chat_uuid")
        if not chat_uuid:
            return None

        await self._notification_service.notify_user(
            chat_uuid,
            {
                "type": EventType.MESSAGE_CREATED,
                "data": payload,
            },
        )
        return "success"

    async def on_user_online(self, payload: Dict[str, Any]) -> Optional[str]:
        user_uuid = payload.get("user_uuid")
        if not user_uuid:
            return None

        await self._notification_service.notify_user(
            user_uuid,
            {
                "type": EventType.USER_ONLINE,
                "data": {"user_uuid": user_uuid, "online": True},
            },
        )
        return "success"

_handler = MessageHandler()
message_handlers = {
    EventType.TYPING: _handler.on_typing,
    EventType.MESSAGE_CREATED: _handler.on_message_created,
    EventType.USER_ONLINE: _handler.on_user_online,
}
