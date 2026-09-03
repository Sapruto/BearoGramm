from typing import Optional, List, Tuple, Dict, Any

from src.general.repository.sql.sql_query import SqlQuery
from src.modules.participants import Permission, PermissionService, ChatAction, MessageAction

from .personal_models import PersonalChatResponse, PersonalChatPreview
from .personal_exceptions import CannotChatWithSelfError
from ..base.base_chat_service import BaseChatService
from ..base.exceptions import (
    UserNotParticipantError,
    PermissionDeniedError,
    InvalidParticipantsError,
    ChatNotFoundError,
)
from ..chat_types import ChatType
from ...core.repositories.chat_repository import ChatRepository
from ...models.entities.chat_entity import ChatFields


class PersonalChatService(BaseChatService):
    def __init__(
            self,
            repository: Optional[ChatRepository] = None,
            permission_service: Optional[PermissionService] = None,
    ):
        super().__init__(repository, permission_service)

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

    async def get_or_create(
            self,
            user_uuid: str,
            other_user_uuid: str
    ) -> PersonalChatResponse:
        if user_uuid == other_user_uuid:
            raise CannotChatWithSelfError()

        existing = await self._repository.find_between_users(user_uuid, other_user_uuid)
        if existing:
            return PersonalChatResponse(
                uuid=existing.uuid,
                partner_uuid=other_user_uuid,
                created_at=existing.created_at,
                updated_at=existing.updated_at,
                metadata=existing.metadata if hasattr(existing, 'metadata') else {}
            )

        chat = await self.create_chat(user_uuid=user_uuid, uuids=[user_uuid, other_user_uuid])

        return PersonalChatResponse(
            uuid=chat.uuid,
            partner_uuid=other_user_uuid,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            metadata=chat.metadata if hasattr(chat, 'metadata') else {}
        )

    async def get_chat(
            self,
            chat_uuid: str,
            user_uuid: str
    ) -> PersonalChatResponse:
        query = SqlQuery[ChatFields]().add_filter(ChatFields.UUID, chat_uuid)
        chat = await self._repository.get(query)

        if not chat:
            raise ChatNotFoundError(chat_uuid)

        await self._ensure_participant(user_uuid, chat_uuid)

        participants = await self._permission_service.get_by_resource(chat_uuid)
        partner_uuid: str = ""
        for p in participants:
            if p.user_uuid != user_uuid:
                partner_uuid = p.user_uuid
                break

        return PersonalChatResponse(
            uuid=chat.uuid,
            partner_uuid=partner_uuid,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            metadata=chat.metadata if hasattr(chat, 'metadata') else {}
        )

    async def get_user_chats(
            self,
            user_uuid: str,
            limit: int = 50,
            offset: int = 0
    ) -> Tuple[List[PersonalChatPreview], int]:
        query = SqlQuery[ChatFields]().add_filter(
            ChatFields.CHAT_TYPE, ChatType.PERSONAL.value
        )
        query.limit = limit
        query.offset = offset

        chats = await self._repository.get_all(query)
        total = await self._repository.count(query)

        previews: List[PersonalChatPreview] = []
        for chat in chats:
            participants = await self._permission_service.get_by_resource(chat.uuid)
            partner_uuid: str = ""
            for p in participants:
                if p.user_uuid != user_uuid:
                    partner_uuid = p.user_uuid
                    break

            previews.append(
                PersonalChatPreview(
                    uuid=chat.uuid,
                    partner_uuid=partner_uuid,
                    updated_at=chat.updated_at
                )
            )

        return previews, total

    async def delete_chat(
            self,
            chat_uuid: str,
            user_uuid: str
    ) -> bool:
        await self._ensure_participant(user_uuid, chat_uuid)

        if not await self._can_delete(user_uuid, chat_uuid):
            raise PermissionDeniedError(user_uuid, "DELETE", chat_uuid)

        query = SqlQuery[ChatFields]().add_filter(ChatFields.UUID, chat_uuid)
        deleted_count: int = await self._repository.delete(query)

        return deleted_count > 0

    async def get_chat_partner(
            self,
            chat_uuid: str,
            user_uuid: str
    ) -> str:
        query = SqlQuery[ChatFields]().add_filter(ChatFields.UUID, chat_uuid)
        chat = await self._repository.get(query)

        if not chat:
            raise ChatNotFoundError(chat_uuid)

        await self._ensure_participant(user_uuid, chat_uuid)

        participants = await self._permission_service.get_by_resource(chat_uuid)
        for p in participants:
            if p.user_uuid != user_uuid:
                return p.user_uuid

        raise UserNotParticipantError(user_uuid, chat_uuid)

    async def is_participant(
            self,
            chat_uuid: str,
            user_uuid: str
    ) -> bool:
        try:
            await self._ensure_participant(user_uuid, chat_uuid)
            return True
        except UserNotParticipantError:
            return False


def get_personal_chat_service() -> PersonalChatService:
    return PersonalChatService()
