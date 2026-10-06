from typing import Optional
from enum import Enum

from .chat_service import ChatService, get_chat_service

from src.modules.event_notification import EventNotificationService, get_notification_event_service


class ChatEventType(str, Enum):
    CREATE = "chat_created"
    DELETE = "chat_deleted"

    def __str__(self):
        return self.value


class NotificatorChatEvents:
    def __init__(self, chat_service: Optional[ChatService] = None, notification_service: Optional[EventNotificationService] = None):
        self._chat_service = chat_service or get_chat_service()
        self._notification_service = notification_service or get_notification_event_service()

    async def notify_about_chat_event(self, chat_uuid: str, event_type: ChatEventType):
        user_uuids = await self._chat_service.get_participant_uuids(chat_uuid)
        await self._notification_service.notify_users(
            user_uuids=user_uuids or [],
            notification={
                "type": event_type.value,
                "data": { "chat_uuid": chat_uuid },
            }
        )


def get_notificator_chat_event() -> NotificatorChatEvents:
    return NotificatorChatEvents()
