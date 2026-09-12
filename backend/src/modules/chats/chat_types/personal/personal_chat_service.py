from typing import Optional, List, Tuple, Dict, Any

from src.general.repository.sql.sql_query import SqlQuery
from src.modules.participants.core.exceptions import NotParticipant
from src.modules.participants.models.enums import ResourceType
from src.modules.profiles_custom import ProfileCustomService, get_profile_custom_service
from src.modules.user import UserServiceAPI, get_user_service_api
from src.modules.participants import Permission, PermissionService, ChatAction, MessageAction

from .personal_models import PersonalChatResponse, PersonalChatPreview
from .personal_exceptions import CannotChatWithSelfError, NotFoundUser, ChatIsExisting
from .personal_repository import get_personal_repository, PersonalRepository
from ..base.base_chat_service import BaseChatService
from ..base.exceptions import (
    UserNotParticipantError,
    PermissionDeniedError,
    InvalidParticipantsError,
    ChatNotFoundError,
)
from ..chat_types import ChatType
from ...models.entities.chat_entity import ChatFields


class PersonalChatService(BaseChatService):
    def __init__(
            self,
            repository: Optional[PersonalRepository] = None,
            permission_service: Optional[PermissionService] = None,
            user_service: Optional[UserServiceAPI] = None,
            profile_service: Optional[ProfileCustomService] = None,
    ):
        self.user_service = user_service or get_user_service_api()
        self.profile_service = profile_service or get_profile_custom_service()
        super().__init__(repository or get_personal_repository(), permission_service)

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

    async def create(
            self,
            user_uuid: str,
            other_user_phone: str
    ) -> PersonalChatResponse:
        user = await self.user_service.get_user_by_phone(other_user_phone)
        if not user:
            raise NotFoundUser()
        other_user_uuid = user.uuid

        if user_uuid == other_user_uuid:
            raise CannotChatWithSelfError()

        existing = await self._repository.get_personal_chat_by_participants([user_uuid, other_user_uuid])
        if existing:
            raise ChatIsExisting()

        chat = await self.create_chat(user_uuid=user_uuid, uuids=[user_uuid, other_user_uuid])

        return PersonalChatResponse(
            uuid=chat.uuid,
            partner_uuid=other_user_uuid,
            created_at=chat.created_at,
            updated_at=chat.updated_at
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

        profiles = self.profile_service.get_by_user_uuids([user_uuid, partner_uuid])

        return PersonalChatResponse(
            uuid=chat.uuid,
            partner_uuid=partner_uuid,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            profiles=profiles
        )

    async def get_user_chats(
            self,
            user_uuid: str,
            limit: int = 50,
            offset: int = 0
    ) -> Tuple[List[PersonalChatPreview], int]:
        query = SqlQuery[ChatFields]().add_filter(
            ChatFields.CHAT_TYPE, ChatType.PERSONAL
        )
        query.limit = limit
        query.offset = offset

        chats = await self._repository.get_all(query)
        total = await self._repository.count(query)

        previews: List[PersonalChatPreview] = []
        for chat in chats:
            try:
                await self._permission_service.validate(user_uuid, chat.uuid, ResourceType.CHAT)
            except NotParticipant:
                continue

            participants = await self._permission_service.get_by_resource(chat.uuid)
            partner_uuid: str = ""
            for p in participants:
                if p.user_uuid != user_uuid:
                    partner_uuid = p.user_uuid
                    break

            partner_profile = await self.profile_service.get_by_user_uuid(partner_uuid)

            previews.append(
                PersonalChatPreview(
                    uuid=chat.uuid,
                    partner_uuid=partner_uuid,
                    partner_profile=partner_profile,
                    updated_at=chat.updated_at,
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

        query = SqlQuery[ChatFields]().add_filter(value=chat_uuid, field=ChatFields.UUID)
        exist = await self._repository.get(query)
        if not exist:
            raise NotFoundUser()

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
