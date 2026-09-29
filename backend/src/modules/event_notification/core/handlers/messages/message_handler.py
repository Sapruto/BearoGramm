from enum import Enum
from typing import Any, Dict, List, Optional

from src.core.logger import get_logger
from src.modules.chats import ChatService, get_chat_service

from ...services.event_notification_service import (
    get_notification_event_service,
    EventNotificationService,
)

logger = get_logger(__name__)


class EventType(str, Enum):
    TYPING = "typing"
    USER_ONLINE = "user_online"

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)


class MessageHandler:
    def __init__(
        self,
        notification_service: Optional[EventNotificationService] = None,
        chat_service: Optional[ChatService] = None,
    ):
        self._notification_service = notification_service or get_notification_event_service()
        self._chat_service = chat_service or get_chat_service()

    async def _get_chat_participants(self, chat_uuid: str) -> List[str]:
        participants = await self._chat_service.get_participants(chat_uuid)
        return [i.user_uuid for i in participants]

    async def on_typing(self, payload: Dict[str, Any]) -> Optional[str]:
        user_uuid = payload.get("user_uuid")
        chat_uuid = payload.get("chat_uuid")
        if not user_uuid or not chat_uuid:
            return None

        recipients = await self._get_chat_participants(chat_uuid)
        recipients = [r for r in recipients if r != user_uuid]

        await self._notification_service.notify_users(
            recipients,
            {
                "type": EventType.TYPING.value,
                "data": {"user_uuid": user_uuid, "chat_uuid": chat_uuid},
            },
        )
        return None

    async def on_user_online(self, payload: Dict[str, Any]) -> Optional[str]:
        user_uuid = payload.get("user_uuid")
        chat_uuids = payload.get("chat_uuids", [])
        if not user_uuid:
            return None

        recipients: List[str] = []
        for chat_uuid in chat_uuids:
            participants = await self._get_chat_participants(chat_uuid)
            recipients.extend(p for p in participants if p != user_uuid)

        recipients = list(set(recipients))

        await self._notification_service.notify_users(
            recipients,
            {
                "type": EventType.USER_ONLINE.value,
                "data": {"user_uuid": user_uuid, "online": True},
            },
        )
        return None


_handler = MessageHandler()
message_handlers = {
    EventType.TYPING: _handler.on_typing,
    EventType.USER_ONLINE: _handler.on_user_online,
}