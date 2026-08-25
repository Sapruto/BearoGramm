from typing import Optional, List, Tuple
from sqlalchemy import and_, func

from src.general.repository.sql.sql_query import SqlQuery

from ..models.personal_access_type import PERSONAL_TYPE
from ..models.personal_contact import PersonalContact
from ....models.orm.chat_orm import ChatORM
from ....models.entities.chat_entity import ChatEntity, ChatFields
from ....core.repositories.chat_repository import ChatRepository
from ....core.db.chat_db import ChatManager

class PersonalChatRepository(ChatRepository):
    def __init__(self, manager: Optional[ChatManager] = None):
        super().__init__(manager)

    async def find_between_users(self, user_uuid: str, companion_uuid: str) -> Optional[ChatEntity]:
        query = SqlQuery[ChatFields]()
        query.add_filter(
            and_(
                ChatORM.access_type == PERSONAL_TYPE,
                ChatORM.accesses.contains([{"user_uuid": user_uuid}]),
                ChatORM.accesses.contains([{"user_uuid": companion_uuid}]),
                func.jsonb_array_length(ChatORM.accesses) == 2
            )
        )
        return await self.get(query)

    async def get_user_chats(self, user_uuid: str, limit: Optional[int] = None, offset: Optional[int] = None) -> Tuple[List[ChatEntity], int]:
        query = SqlQuery[ChatFields]()
        query.add_filter(
            and_(
                ChatORM.access_type == PERSONAL_TYPE,
                ChatORM.accesses.contains([{"user_uuid": user_uuid}]),
                func.jsonb_array_length(ChatORM.accesses) == 2
            )
        )

        total = await self.count(query)

        query.limit = limit
        query.offset = offset

        query.order_by = [(ChatFields.UPDATED_AT, 'desc')]

        chats = await self.get_all(query)
        return chats, total

    async def get_contacts_with_status(self, user_uuid: str, limit: Optional[int] = None, offset: Optional[int] = None) -> Tuple[List[PersonalContact], int]:
        chats, total = await self.get_user_chats(user_uuid, limit, offset)

        contacts = []
        for chat in chats:
            other_user = None
            other_access = None

            for access in chat.accesses:
                if access.user_uuid != user_uuid:
                    other_user = access.user_uuid
                    other_access = access
                    break

            if other_user and other_access:
                contacts.append(PersonalContact(chat_uuid=chat.uuid,
                    user_uuid=other_user,
                    is_blocked=other_access.is_blocked,
                    last_message_at=other_access.last_message_at,
                    unread_count=other_access.unread_count,
                    created_at=chat.created_at,
                    updated_at=chat.updated_at
                ))

        return contacts, total

    async def get_all_user_chats_raw(self, user_uuid: str) -> List[ChatEntity]:
        query = SqlQuery[ChatFields]()
        query.add_filter(
            and_(
                ChatORM.access_type == PERSONAL_TYPE,
                ChatORM.accesses.contains([{"user_uuid": user_uuid}]),
                func.jsonb_array_length(ChatORM.accesses) == 2
            )
        )
        return await self.get_all(query)

    async def count_user_chats(self, user_uuid: str) -> int:
        query = SqlQuery[ChatFields]()
        query.add_filter(
            and_(
                ChatORM.access_type == PERSONAL_TYPE,
                ChatORM.accesses.contains([{"user_uuid": user_uuid}]),
                func.jsonb_array_length(ChatORM.accesses) == 2
            )
        )
        return await self.count(query)

    async def exists_between_users(self, user_uuid: str, companion_uuid: str) -> bool:
        chat = await self.find_between_users(user_uuid, companion_uuid)
        return chat is not None

def get_personal_chat_repository() -> PersonalChatRepository:
    return PersonalChatRepository()
