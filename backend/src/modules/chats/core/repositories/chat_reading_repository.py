from typing import Optional

from src.general.repository.sql.sql_base_repository import BaseRepository

from ...models.entities.chat_reading_entity import ChatReadingEntity, ChatReadingFields

from .mappers.chat_reading_mapper import ChatReadingMapper
from ..db.chat_reading_db import ChatReadingManager, get_chat_reading_manager


class ChatReadingRepository(BaseRepository[ChatReadingManager, ChatReadingFields, ChatReadingEntity]):
    def __init__(self, manager: Optional[ChatReadingManager] = None):
        mapper = ChatReadingMapper()
        super().__init__(manager=manager or get_chat_reading_manager(), mapper=mapper)


def get_chat_reading_repository() -> ChatReadingRepository:
    return ChatReadingRepository()
