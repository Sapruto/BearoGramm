from typing import Optional
from enum import Enum

from src.general.repository.sql.sql_query import SqlQuery
from src.modules.chats.core.services.chat_service import ChatService, get_chat_service
from ..repositories.friend_repository import FriendRepository, get_friend_repository
from ...models.entities.friend_entity import FriendFields, FriendEntity

from src.modules.event_notification import EventNotificationService, get_notification_event_service


class FriendEventType(str, Enum):
    NEW_REQUEST = "new_request"
    CHANGED_STATUS = "changed_status"

    def __str__(self):
        return self.value


class NotificatorFriendEvents:
    def __init__(self, friend_repository: Optional[FriendRepository] = None, notification_service: Optional[EventNotificationService] = None):
        self._friend_repository = friend_repository or get_friend_repository()
        self._notification_service = notification_service or get_notification_event_service()

    async def notify_about_message_event_by_uuid(self, friend_uuid: str, event_type: FriendEventType):
        friend = await self._friend_repository.get(SqlQuery[FriendFields]().add_filter(field=FriendFields.UUID, value=friend_uuid))
        if not friend:
            return
        await self.notify_about_friend_event(friend, event_type)

    async def notify_about_friend_event(self, friend: FriendEntity, event_type: FriendEventType):
        await self._notification_service.notify_users(
            user_uuids=friend.user_uuid1 or [],
            notification={
                "type": event_type.value,
                "data": friend.model_dump(mode="json"),
            },
        )


def get_notificator_friend_event() -> NotificatorFriendEvents:
    return NotificatorFriendEvents()
