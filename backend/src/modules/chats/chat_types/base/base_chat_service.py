from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime

from src.modules.participants import (
    Permission,
    PermissionService,
    get_permission_service,
    ResourceType,
    ChatAction,
    MessageAction
)

from ...core.repositories.chat_repository import ChatRepository, get_chat_repository
from ...models.entities.chat_entity import ChatEntity
from .exceptions import (
    ChatNotFoundError,
    UserNotParticipantError,
    PermissionDeniedError,
    CreatorMustBeParticipantError,
    DuplicateParticipantsError,
    InvalidParticipantsError,
)


class BaseChatService(ABC):
    def __init__(
            self,
            repository: Optional[ChatRepository] = None,
            permission_service: Optional[PermissionService] = None,
    ):
        self._repository = repository or get_chat_repository()
        self._permission_service = permission_service or get_permission_service()

    @abstractmethod
    def _get_chat_type(self) -> str:
        pass

    @abstractmethod
    async def _validate_participants(self, participants: List[str]) -> None:
        """
        raise: InvalidParticipantsError
        IF F*CKING PARTICIPANT IS INVALID
        """
        pass

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

    async def _can_delete(self, user_uuid: str, chat_uuid: str) -> bool:
        return await self._permission_service.validate(
            user_uuid, chat_uuid, ResourceType.CHAT, ChatAction.DELETE
        )

    async def _can_manage(self, user_uuid: str, chat_uuid: str) -> bool:
        return await self._permission_service.validate(
            user_uuid, chat_uuid, ResourceType.CHAT, ChatAction.MANAGE
        )

    async def _ensure_participant(self, user_uuid: str, chat_uuid: str) -> None:
        participant = await self._permission_service.get_by_user_resource(
            user_uuid, chat_uuid, ResourceType.CHAT
        )
        if not participant:
            raise UserNotParticipantError(user_uuid, chat_uuid)

    async def create_chat(
            self,
            user_uuid: str,
            uuids: List[str],
            permissions_map: Optional[Dict[str, List[Permission]]] = None,
            context: Optional[Dict[str, Any]] = None,
    ) -> ChatEntity:
        if user_uuid not in uuids:
            raise CreatorMustBeParticipantError()

        if len(set(uuids)) != len(uuids):
            raise DuplicateParticipantsError()

        await self._validate_participants(uuids)

        chat = ChatEntity(
            uuid=str(uuid4()),
            access_type=self._get_chat_type(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        saved_chat = await self._repository.save(chat)

        for participant_uuid in uuids:
            permissions = permissions_map.get(participant_uuid) if permissions_map else None
            if permissions is None:
                permissions = self._get_default_permissions(participant_uuid, context)

            await self._permission_service.create(
                user_uuid=participant_uuid,
                resource_uuid=saved_chat.uuid,
                resource_type=ResourceType.CHAT,
                permissions=permissions,
            )

        return saved_chat

    async def get_chat(self, chat_uuid: str, user_uuid: str) -> ChatEntity:
        chat = await self._repository.get_by_uuid(chat_uuid)
        if not chat:
            raise ChatNotFoundError(chat_uuid)

        await self._ensure_participant(user_uuid, chat_uuid)

        return chat

    async def get_chats_for_user(
            self,
            user_uuid: str,
            limit: int = 50,
            offset: int = 0,
    ) -> tuple[List[ChatEntity], int]:
        return await self._repository.get_user_chats_paginated(
            user_uuid, limit, offset, chat_type=self._get_chat_type()
        )

    async def get_contact_list(
            self,
            user_uuid: str,
            limit: int = 50,
            offset: int = 0,
    ) -> tuple[List[Dict], int]:
        return await self._repository.get_contacts_paginated(
            user_uuid, limit, offset
        )

    async def delete_chat(self, chat_uuid: str, user_uuid: str) -> None:
        await self._ensure_participant(user_uuid, chat_uuid)

        if not await self._can_delete(user_uuid, chat_uuid):
            raise PermissionDeniedError(user_uuid, "DELETE", chat_uuid)

        await self._repository.delete_by_uuid(chat_uuid)

    async def add_permissions(
            self,
            chat_uuid: str,
            from_user_uuid: str,
            to_user_uuid: str,
            permissions: List[Permission],
    ) -> None:
        if not await self._can_manage(from_user_uuid, chat_uuid):
            raise PermissionDeniedError(from_user_uuid, "MANAGE", chat_uuid)

        participant = await self._permission_service.get_by_user_resource(
            to_user_uuid, chat_uuid, ResourceType.CHAT
        )
        if not participant:
            raise UserNotParticipantError(to_user_uuid, chat_uuid)

        current_perms = participant.permissions
        for perm in permissions:
            current_perms[perm.action] = perm.enabled

        await self._permission_service.update(participant.uuid, [
            Permission(action=k, enabled=v) for k, v in current_perms.items()
        ])

    async def remove_permissions(
            self,
            chat_uuid: str,
            from_user_uuid: str,
            to_user_uuid: str,
            permissions: List[Permission],
    ) -> None:
        if not await self._can_manage(from_user_uuid, chat_uuid):
            raise PermissionDeniedError(from_user_uuid, "MANAGE", chat_uuid)

        participant = await self._permission_service.get_by_user_resource(
            to_user_uuid, chat_uuid, ResourceType.CHAT
        )
        if not participant:
            raise UserNotParticipantError(to_user_uuid, chat_uuid)

        current_perms = participant.permissions
        for perm in permissions:
            current_perms.pop(perm.action, None)

        await self._permission_service.update(participant.uuid, [
            Permission(action=k, enabled=v) for k, v in current_perms.items()
        ])
