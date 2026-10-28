from typing import Optional
from enum import Enum

from src.general.repository.sql.sql_query import SqlQuery
from ..repositories.friend_repository import FriendRepository, get_friend_repository
from ...models.entities.friend_entity import FriendFields, FriendEntity

from src.modules.event_notification import EventNotificationService, get_notification_event_service


class FriendEventType(str, Enum):
    NEW_REQUEST = "new_request"
    CHANGED_STATUS = "changed_status"

    def __str__(self):
        return self.value


class NotificatorFriendEvents:
    def __init__(self,
                 friend_repository: Optional[FriendRepository] = None,
                 notification_service: Optional[EventNotificationService] = None
                 ):
        self._friend_repository = friend_repository or get_friend_repository()
        self._notification_service = notification_service or get_notification_event_service()
        self._prefix = "friend:"

    async def notify_about_friend_event_by_uuid(self, from_user_uuid: str, friend_uuid: str,
                                                event_type: FriendEventType):
        friend = await self._friend_repository.get(
            SqlQuery[FriendFields]().add_filter(field=FriendFields.UUID, value=friend_uuid))
        if not friend:
            return
        await self.notify_about_friend_event(from_user_uuid, friend, event_type)

    async def notify_about_friend_event(self, from_user_uuid: str, friend: FriendEntity, event_type: FriendEventType):
        for_user_uuid = friend.user_uuid1 if from_user_uuid != friend.user_uuid1 else friend.user_uuid2
        await self._notification_service.notify_users(
            user_uuids=[for_user_uuid],
            notification={
                "type": self._prefix + event_type.value,
                "data": friend.model_dump(mode="json"),
            },
        )


def get_notificator_friend_event() -> NotificatorFriendEvents:
    return NotificatorFriendEvents()
