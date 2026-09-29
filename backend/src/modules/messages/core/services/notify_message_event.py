from typing import Optional
from enum import Enum

from src.general.repository.sql.sql_query import SqlQuery
from src.modules.chats.core.services.chat_service import ChatService, get_chat_service
from ..repositories.message_repository import MessageRepository, get_message_repository
from ...models.entities.message_entity import MessageFields, MessageEntity

from src.modules.event_notification import EventNotificationService, get_notification_event_service


class MessageEventType(str, Enum):
    CREATE = "message_created"
    UPDATE = "message_updated"
    DELETE = "message_deleted"

    def __str__(self):
        return self.value


class NotificatorMessageEvents:
    def __init__(self, _message_repository: Optional[MessageRepository] = None, chat_service: Optional[ChatService] = None, notification_service: Optional[EventNotificationService] = None):
        self._message_repository = _message_repository or get_message_repository()
        self._chat_service = chat_service or get_chat_service()
        self._notification_service = notification_service or get_notification_event_service()

    async def notify_about_message_event_by_uuid(self, message_uuid: str, event_type: MessageEventType):
        message = await self._message_repository.get(SqlQuery[MessageFields]().add_filter(field=MessageFields.UUID, value=message_uuid))
        if not message:
            return
        await self.notify_about_message_event(message, event_type)

    async def notify_about_message_event(self, message: MessageEntity, event_type: MessageEventType):
        user_uuids = await self._chat_service.get_participant_uuids(message.chat_uuid)

        if event_type == MessageEventType.DELETE:
            await self._notification_service.notify_users(
                user_uuids=user_uuids or [],
                notification={
                    "type": event_type.value,
                    "data": message.uuid,
                },
            )

        await self._notification_service.notify_users(
            user_uuids=user_uuids or [],
            notification={
                "type": event_type.value,
                "data": message.model_dump(mode="json"),
            },
        )


def get_notificator_message_event() -> NotificatorMessageEvents:
    return NotificatorMessageEvents()
