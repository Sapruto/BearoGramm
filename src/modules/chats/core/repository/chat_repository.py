from src.general.repository.sql.sql_base_repository import BaseRepository
from typing import Optional

from .mappers.chat_mapper import ChatMapper
from ..db.chat_db import ChatManager, get_chat_manager
from ...models.entities.chat_entity import ChatFields, ChatEntity

class ChatRepository(BaseRepository[ChatManager, ChatFields, ChatEntity]):
    def __init__(self, manager: Optional[ChatManager] = None):
        mapper = ChatMapper()
        super().__init__(manager=manager or get_chat_manager(), mapper=mapper)

def get_chat_repository() -> ChatRepository:
    return ChatRepository()
