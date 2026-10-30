from typing import Optional
from uuid import uuid4

from sqlalchemy.sql.functions import now

from src.general.repository.sql.sql_base_repository import BaseRepository
from src.general.repository.sql.sql_query import SqlQuery

from ...models.entities.chat_reading_entity import ChatReadingEntity, ChatReadingFields

from .mappers.chat_reading_mapper import ChatReadingMapper
from ..db.chat_reading_db import ChatReadingManager, get_chat_reading_manager


class ChatReadingRepository(BaseRepository[ChatReadingManager, ChatReadingFields, ChatReadingEntity]):
    def __init__(self, manager: Optional[ChatReadingManager] = None):
        mapper = ChatReadingMapper()
        super().__init__(manager=manager or get_chat_reading_manager(), mapper=mapper)

    async def upsert_last_read(
        self, chat_uuid, user_uuid, last_read_message_uuid
    ) -> ChatReadingEntity:
        existing = await self.get(
            SqlQuery(filters={
                ChatReadingFields.CHAT_UUID: chat_uuid,
                ChatReadingFields.USER_UUID: user_uuid,
            })
        )
        if existing is None:
            entity = ChatReadingEntity(
                uuid=uuid4(),
                chat_uuid=chat_uuid,
                user_uuid=user_uuid,
                last_read_message_uuid=last_read_message_uuid,
                updated_at=now(),
            )
            return await self.save(entity, to_update=False)
        existing.last_read_message_uuid = last_read_message_uuid
        existing.updated_at = now()
        return await self.save(existing, to_update=True)


def get_chat_reading_repository() -> ChatReadingRepository:
    return ChatReadingRepository()
