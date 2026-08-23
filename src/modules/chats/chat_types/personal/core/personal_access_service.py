from typing import Optional, List
from uuid import uuid4
from datetime import datetime
from sqlalchemy import and_, func

from src.general.repository.sql.sql_query import SqlQuery

from ..models.personal_access_type import PersonalAccessType, PERSONAL_TYPE
from ..models.personal_contact import PersonalContact
from ....models.orm.chat_orm import ChatORM
from ....models.entities.chat_entity import ChatEntity
from ....core.repository.chat_repository import ChatRepository, get_chat_repository

class PersonalAccessService:
    def __init__(self, repo: Optional[ChatRepository] = None):
        self.repo = repo or get_chat_repository()

    async def create_personal_chat(self, user_uuid: str, companion_uuid: str) -> ChatEntity:
        if user_uuid == companion_uuid:
            raise ValueError("You can't create chat with bipolarca")

        existing = await self.find_chat_between_users(user_uuid, companion_uuid)
        if existing:
            raise ValueError(f"Chat was created")

        chat = ChatEntity(
            uuid=str(uuid4()),
            accesses=[
                PersonalAccessType(user_uuid=user_uuid),
                PersonalAccessType(user_uuid=companion_uuid)
            ]
        )

        return await self.repo.save(chat)

    async def get_by_uuid(self, chat_uuid: str) -> Optional[ChatEntity]:
        query = SqlQuery().add_filter(ChatORM.uuid == chat_uuid)
        return await self.repo.get(query)

    async def get_personal_chat(self, chat_uuid: str, user_uuid: str) -> Optional[ChatEntity]:
        chat = await self.get_by_uuid(chat_uuid)
        if not chat:
            return None

        if not self.is_user_in_chat(chat, user_uuid):
            return None

        if not self._validate_personal_chat(chat):
            return None

        return chat

    async def get_chats_for_user(self, user_uuid: str) -> List[ChatEntity]:
        query = SqlQuery(limit=100)
        query.add_filter(
            and_(
                ChatORM.access_type == PERSONAL_TYPE,
                ChatORM.accesses.contains([{"user_uuid": user_uuid}])
            )
        )
        chats = await self.repo.get_all(query)
        return [c for c in chats if self._validate_personal_chat(c)]

    async def get_contact_list(self, user_uuid: str) -> List[PersonalContact]:
        chats = await self.get_chats_for_user(user_uuid)
        contacts = []

        for chat in chats:
            other_user = self.get_other_user(chat, user_uuid)
            if not other_user:
                continue

            other_access = self.get_user_access(chat, other_user)
            if not other_access:
                continue

            contacts.append(
                PersonalContact(
                    chat_uuid=chat.uuid,
                    user_uuid=other_user,
                    is_blocked=other_access.is_blocked if other_access else False,
                    last_message_at=other_access.last_message_at if other_access else None,
                    unread_count=other_access.unread_count if other_access else 0,
                    created_at=chat.created_at,
                    updated_at=chat.updated_at
                )
            )

        return sorted(
            contacts,
            key=lambda x: x["last_message_at"] or datetime.min,
            reverse=True
        )

    async def find_chat_between_users(self, user_uuid: str, companion_uuid: str) -> Optional[ChatEntity]:
        query = SqlQuery()
        query.add_filter(
            and_(
                ChatORM.access_type == PERSONAL_TYPE,
                ChatORM.accesses.contains([{"user_uuid": user_uuid}]),
                ChatORM.accesses.contains([{"user_uuid": companion_uuid}]),
                func.jsonb_array_length(ChatORM.accesses) == 2
            )
        )
        return await self.repo.get(query)

    async def block_user_in_chat(self, chat: ChatEntity, blocker_uuid: str, blocked_uuid: str) -> ChatEntity:
        if not self.is_user_in_chat(chat, blocker_uuid):
            raise ValueError(f"User {blocker_uuid} not in chat")

        blocked_access = self.get_user_access(chat, blocked_uuid)
        if not blocked_access:
            raise ValueError(f"User {blocked_uuid} not found in chat")

        blocked_access.is_blocked = True
        blocked_access.blocked_at = datetime.now()
        blocked_access.blocked_by = blocker_uuid

        return await self.repo.save(chat)

    async def unblock_user_in_chat(self, chat: ChatEntity, user_uuid: str) -> ChatEntity:
        user_access = self.get_user_access(chat, user_uuid)
        if not user_access:
            raise ValueError(f"User {user_uuid} not found in chat")

        user_access.is_blocked = False
        user_access.blocked_at = None
        user_access.blocked_by = None

        return await self.repo.save(chat)

    async def delete_chat(self, chat_uuid: str) -> None:
        query = SqlQuery().add_filter(ChatORM.uuid == chat_uuid)
        await self.repo.delete(query)

    def is_user_in_chat(self, chat: ChatEntity, user_uuid: str) -> bool:
        return any(a.user_uuid == user_uuid for a in chat.accesses)

    def get_user_access(self, chat: ChatEntity, user_uuid: str) -> Optional[PersonalAccessType]:
        for access in chat.accesses:
            if access.user_uuid == user_uuid:
                return access
        return None

    def get_other_user(self, chat: ChatEntity, user_uuid: str) -> Optional[str]:
        participants = [a.user_uuid for a in chat.accesses]
        if len(participants) != 2:
            return None
        return participants[0] if participants[0] != user_uuid else participants[1]

    def _validate_personal_chat(self, chat: ChatEntity) -> bool:
        return len(chat.accesses) == 2 and len(set(a.user_uuid for a in chat.accesses)) == 2

    def get_participants(self, chat: ChatEntity) -> List[str]:
        return [a.user_uuid for a in chat.accesses]

def get_personal_access_service() -> PersonalAccessService:
    return PersonalAccessService()

#THIS IS FUCKING STUPED KAL. And we need refactor this stuped service with new repo in the minimodule personal and там сделать крутую шнягу а  не во это дерьмо как сейчас но в целом работает пуфигу.
