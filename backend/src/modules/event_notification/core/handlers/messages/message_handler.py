from enum import Enum
from typing import Any, Dict, List, Optional

from src.core.logger import get_logger
from src.modules.chats import ChatService, get_chat_service
from src.modules.chats.core.services.chat_reading_service import ChatReadingService, get_chat_reading_service, \
    LastReadMessageUuidNotFound
from src.modules.chats.participants import get_permission_service
from src.modules.messages.core.services.message_service import get_message_service

from ...services.event_notification_service import (
    get_notification_event_service,
    EventNotificationService,
)

logger = get_logger(__name__)


class EventType(str, Enum):
    TYPING = "typing"
    USER_ONLINE = "user_online"
    LAST_READ_MESSAGE = "last_read_message"

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)


class MessageHandler:
    def __init__(
        self,
        notification_service: Optional[EventNotificationService] = None,
        chat_service: Optional[ChatService] = None,
        chat_reading_service: Optional[ChatReadingService] = None,
    ):
        self._notification_service = notification_service or get_notification_event_service()
        self._chat_service = chat_service or get_chat_service()
        self._chat_reading_service = chat_reading_service or (
            get_chat_reading_service(
                get_message_service(
                    get_permission_service(),
                    get_chat_service()
                )
            )
        )

    async def _get_chat_participants(self, chat_uuid: str) -> List[str]:
        participants = await self._chat_service.get_participants(chat_uuid)
        return [i.user_uuid for i in participants]

    async def on_typing(self, payload: Dict[str, Any]) -> None:
        user_uuid = payload.get("user_uuid")
        chat_uuid = payload.get("chat_uuid")
        if not isinstance(user_uuid, str) or not isinstance(chat_uuid, str):
            return

        recipients = await self._get_chat_participants(chat_uuid)

        if user_uuid not in recipients:
            return

        recipients = [r for r in recipients]

        await self._notification_service.notify_users(
            recipients,
            {
                "type": EventType.TYPING.value,
                "data": {"user_uuid": user_uuid, "chat_uuid": chat_uuid},
            },
        )

    async def on_user_online(self, payload: Dict[str, Any]) -> Optional[str]:
        user_uuid = payload.get("user_uuid")
        chat_uuids = payload.get("chat_uuids", [])
        if not user_uuid:
            return None

        recipients: List[str] = []
        for chat_uuid in chat_uuids:
            participants = await self._get_chat_participants(chat_uuid)
            recipients.extend(p for p in participants)

        recipients = list(set(recipients))

        await self._notification_service.notify_users(
            recipients,
            {
                "type": EventType.USER_ONLINE.value,
                "data": {"user_uuid": user_uuid, "online": True},
            },
        )
        return None

    async def on_last_read_message(self, payload: Dict[str, Any]) -> None:
        user_uuid = payload.get("user_uuid")
        chat_uuid = payload.get("chat_uuid")
        last_read_message_uuid = payload.get("last_read_message_uuid")
        if not isinstance(user_uuid, str) or not isinstance(chat_uuid, str):
            return

        recipients = await self._get_chat_participants(chat_uuid)

        if user_uuid not in recipients:
            return

        try:
            await self._chat_reading_service.mark_read(user_uuid, chat_uuid, last_read_message_uuid)
        except LastReadMessageUuidNotFound:
            pass

        await self._notification_service.notify_users(
            recipients,
            {
                "type": EventType.LAST_READ_MESSAGE.value,
                "data": {"user_uuid": user_uuid, "last_read_message": last_read_message_uuid or "ALL"},
            },
        )


_handler = MessageHandler()
message_handlers = {
    EventType.TYPING: _handler.on_typing,
    EventType.USER_ONLINE: _handler.on_user_online,
    EventType.LAST_READ_MESSAGE: _handler.on_last_read_message,
}
