from typing import Protocol, List, Tuple, Optional, Dict

from .personal_models import PersonalChatResponse, PersonalChatPreview, GetChatPartnerResponse
from ..base.exceptions import ChatNotFoundError, UserNotParticipantError, PermissionDeniedError
from ...models.entities.chat_entity import ChatEntity
from ...core.services.notify_chat_event import ChatEventType
from ...participants import ChatAction
from ...participants.models.enums import ResourceType, ActionTypification
from ...participants.models.entities.participant_entity import ParticipantEntity
from ...participants.models.entities.permission import Permission


class PersonalProtocol(Protocol):
    async def get_chat_by_uuid(self, chat_uuid: str) -> Optional[ChatEntity]:
        pass

    async def get_user_chats(
            self,
            user_uuid: str,
            limit: int,
            offset: int,
    ) -> Tuple[List[ChatEntity], int]:
        pass

    async def delete_chat_by_uuid(self, chat_uuid: str) -> int:
        pass

    async def get_participants(self, chat_uuid: str) -> List[ParticipantEntity]:
        pass

    async def get_participants_bulk(
            self,
            chat_uuids: List[str]
    ) -> Dict[str, List[ParticipantEntity]]:
        pass

    async def notify(self, chat_uuid: str, event_type: ChatEventType) -> None:
        pass


class PermissionProtocol(Protocol):
    async def create(
            self,
            user_uuid: str,
            resource_uuid: str,
            resource_type: ResourceType,
            permissions: Optional[List[Permission]] = None
    ) -> ParticipantEntity:
        pass

    async def get(
            self,
            uuid: str
    ) -> ParticipantEntity:
        pass

    async def get_by_user_resource(
            self,
            user_uuid: str,
            resource_uuid: str,
            resource_type: ResourceType
    ) -> Optional[ParticipantEntity]:
        pass

    async def get_by_user(
            self,
            user_uuid: str
    ) -> List[ParticipantEntity]:
        pass

    async def get_by_resource(
            self,
            resource_uuid: str
    ) -> List[ParticipantEntity]:
        pass

    async def get_by_resources(
            self,
            resource_uuids: List[str],
            resource_type: Optional[ResourceType] = None,
    ) -> Dict[str, List[ParticipantEntity]]:
        pass

    async def update(
            self,
            uuid: str,
            permissions: List[Permission]
    ) -> ParticipantEntity:
        pass

    async def delete(
            self,
            uuid: str
    ) -> bool:
        pass

    async def validate(
            self,
            user_uuid: str,
            resource_uuid: str,
            resource_type: ResourceType,
            action: Optional[ActionTypification] = None,
    ) -> bool:
        pass


class ProfileProtocol(Protocol):
    async def get_by_user_uuid(self, user_uuid: str):
        pass

    async def get_by_user_uuids(self, user_uuids: List[str]) -> dict:
        pass


class ChatReadingProtocol(Protocol):
    async def get_unread_count(self, chat_uuid: str, user_uuid: str) -> int:
        pass


class PersonalUseCases:
    def __init__(
            self,
            personal_protocol: PersonalProtocol,
            permission_protocol: PermissionProtocol,
            profile_protocol: ProfileProtocol,
            chat_reading_protocol: ChatReadingProtocol,
    ):
        self._personal = personal_protocol
        self._permission = permission_protocol
        self._profile = profile_protocol
        self._reading = chat_reading_protocol

    async def _ensure_participant(
            self,
            user_uuid: str,
            chat_uuid: str
    ) -> None:
        await self._permission.validate(
            user_uuid=user_uuid,
            resource_uuid=chat_uuid,
            resource_type=ResourceType.CHAT,
        )

    async def get_chat(
            self,
            chat_uuid: str,
            user_uuid: str
    ) -> PersonalChatResponse:
        chat = await self._personal.get_chat_by_uuid(chat_uuid)
        if not chat:
            raise ChatNotFoundError(chat_uuid)

        await self._ensure_participant(user_uuid, chat_uuid)

        participants = await self._personal.get_participants(chat_uuid)
        partner_uuid = next(
            (p.user_uuid for p in participants if p.user_uuid != user_uuid),
            None,
        )
        if partner_uuid is None:
            raise UserNotParticipantError(user_uuid, chat_uuid)

        partner_profile = await self._profile.get_by_user_uuid(partner_uuid)

        return PersonalChatResponse(
            uuid=chat.uuid,
            partner_uuid=partner_uuid,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            partner_profile=partner_profile,
        )

    async def get_user_personal_chats(
            self,
            user_uuid: str,
            limit: int = 50,
            offset: int = 0,
    ) -> Tuple[List[PersonalChatPreview], int]:
        chats, total = await self._personal.get_user_chats(
            user_uuid=user_uuid,
            limit=limit,
            offset=offset,
        )
        if not chats:
            return [], total

        chat_uuids = [c.uuid for c in chats]
        participants_by_chat = await self._personal.get_participants_bulk(chat_uuids)

        partner_by_chat: dict[str, str] = {}
        partner_uuids: set[str] = set()
        for chat in chats:
            for p in participants_by_chat.get(chat.uuid, []):
                if p.user_uuid != user_uuid:
                    partner_by_chat[chat.uuid] = p.user_uuid
                    partner_uuids.add(p.user_uuid)
                    break

        profiles_by_uuid = await self._profile.get_by_user_uuids(list(partner_uuids))

        previews: List[PersonalChatPreview] = []
        for chat in chats:
            partner_uuid = partner_by_chat.get(chat.uuid)
            if partner_uuid is None:
                continue
            partner_profile = profiles_by_uuid.get(partner_uuid)
            if partner_profile is None:
                continue
            previews.append(
                PersonalChatPreview(
                    uuid=chat.uuid,
                    partner_uuid=partner_uuid,
                    partner_profile=partner_profile,
                    created_at=chat.created_at,
                    updated_at=chat.updated_at,
                    last_message_at=chat.last_message_at,
                    unread_count=await self._reading.get_unread_count(chat.uuid, user_uuid),
                )
            )

        return previews, total

    async def delete_chat(
            self,
            chat_uuid: str,
            user_uuid: str
    ) -> bool:
        await self._ensure_participant(user_uuid, chat_uuid)

        can_delete = await self._permission.validate(
            user_uuid=user_uuid,
            resource_uuid=chat_uuid,
            resource_type=ResourceType.CHAT,
            action=ChatAction.DELETE,
        )
        if not can_delete:
            raise PermissionDeniedError(user_uuid, ChatAction.DELETE, chat_uuid)

        chat = await self._personal.get_chat_by_uuid(chat_uuid)
        if not chat:
            raise ChatNotFoundError(chat_uuid)

        deleted_count = await self._personal.delete_chat_by_uuid(chat_uuid)
        await self._personal.notify(chat_uuid, ChatEventType.DELETE)
        return deleted_count > 0

    async def get_chat_partner(
            self,
            chat_uuid: str,
            user_uuid: str
    ) -> GetChatPartnerResponse:
        chat = await self._personal.get_chat_by_uuid(chat_uuid)
        if not chat:
            raise ChatNotFoundError(chat_uuid)

        await self._ensure_participant(user_uuid, chat_uuid)

        participants = await self._personal.get_participants(chat_uuid)
        for p in participants:
            if p.user_uuid != user_uuid:
                profile = await self._profile.get_by_user_uuid(p.user_uuid)
                return GetChatPartnerResponse(partner_uuid=p.user_uuid, partner_profile=profile)

        raise UserNotParticipantError(user_uuid, chat_uuid)
