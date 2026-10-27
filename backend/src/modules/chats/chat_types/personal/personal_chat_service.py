from typing import Optional, List, Tuple, Dict, Any

from src.general.repository.sql.sql_query import SqlQuery
from src.modules.friends.core.services.friend_service import NotFriends
from src.modules.chats.participants.models.enums import ResourceType
from src.modules.chats.participants import Permission, PermissionService, ChatAction, MessageAction

from .personal_exceptions import CannotChatWithSelfError, ChatIsExisting
from src.modules.chats.core.repositories.chat_repository import get_chat_repository, ChatRepository
from ..base.base_chat_service import BaseChatService
from ..base.exceptions import InvalidParticipantsError
from ..chat_types import ChatType
from ...core.services.notify_chat_event import get_notificator_chat_event, NotificatorChatEvents, ChatEventType
from ...models.entities.chat_entity import ChatFields, ChatEntity


class PersonalChatService(BaseChatService):
    def __init__(
            self,
            repository: Optional[ChatRepository] = None,
            permission_service: Optional[PermissionService] = None,
            notify_service: Optional[NotificatorChatEvents] = None,
            max_limit: Optional[int] = None,
    ):
        self._notify_service = notify_service or get_notificator_chat_event()
        self._max_limit = max_limit or 50
        super().__init__(repository or get_chat_repository(), permission_service)

    def _get_chat_type(self) -> str:
        return ChatType.PERSONAL.value

    async def _validate_participants(self, participants: List[str]) -> None:
        if len(participants) != 2:
            raise InvalidParticipantsError(
                f"Personal chat must have exactly 2 participants, got {len(participants)}"
            )

    def _get_default_permissions(
            self,
            user_uuid: str,
            context: Optional[Dict[str, Any]] = None
    ) -> List[Permission]:
        return [
            Permission(action=ChatAction.CREATE, enabled=True),
            Permission(action=ChatAction.GET, enabled=True),
            Permission(action=ChatAction.DELETE, enabled=True),
            Permission(action=ChatAction.MANAGE, enabled=True),
            Permission(action=MessageAction.CREATE, enabled=True),
            Permission(action=MessageAction.GET, enabled=True),
            Permission(action=MessageAction.UPDATE, enabled=True),
            Permission(action=MessageAction.DELETE, enabled=True),
        ]

    async def create_by_uuid_with_bool(self, user_uuid: str, other_user_uuid: str) -> bool:
        try:
            if user_uuid == other_user_uuid:
                raise CannotChatWithSelfError()

            existing = await self._repository.get_chat_by_participants([user_uuid, other_user_uuid], self._get_chat_type())
            if existing:
                raise ChatIsExisting()

            chat = await self.create_chat(user_uuid=user_uuid, uuids=[user_uuid, other_user_uuid])
            await self._notify_service.notify_about_chat_event(chat.uuid, ChatEventType.CREATE)

            return True

        except (CannotChatWithSelfError, ChatIsExisting, NotFriends):
            return False

    async def get_chat_by_uuid(self, chat_uuid: str) -> Optional[ChatEntity]:
        query = SqlQuery[ChatFields]().add_filter(ChatFields.UUID, chat_uuid)
        return await self._repository.get(query)

    async def get_user_chats(
            self,
            user_uuid: str,
            limit: int,
            offset: int,
    ) -> Tuple[List[ChatEntity], int]:
        return await self._repository.get_user_chats(
            user_uuid=user_uuid,
            limit=min(self._max_limit, limit),
            offset=offset,
            show_new=True,
            chat_type=self._get_chat_type(),
        )

    async def delete_chat_by_uuid(self, chat_uuid: str) -> int:
        query = SqlQuery[ChatFields]().add_filter(ChatFields.UUID, chat_uuid)
        return await self._repository.delete(query)

    async def get_participants(self, chat_uuid: str) -> List:
        return await self._permission_service.get_by_resource(chat_uuid)

    async def get_participants_bulk(self, chat_uuids: List[str]) -> dict:
        return await self._permission_service.get_by_resources(
            resource_uuids=chat_uuids,
            resource_type=ResourceType.CHAT,
        )

    async def notify(self, chat_uuid: str, event_type: ChatEventType) -> None:
        await self._notify_service.notify_about_chat_event(chat_uuid, event_type)


def get_personal_chat_service() -> PersonalChatService:
    return PersonalChatService()
