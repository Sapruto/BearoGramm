from src.general.repository.sql.sql_base_repository import BaseRepository
from typing import Optional

from .chat_custom_mapper import ChatCustomMapper
from src.modules.chats.chat_custom.core.db.chat_custom_db import ChatCustomManager, get_chat_custom_manager
from src.modules.chats.chat_custom.models.entities.chat_custom_entity import ChatCustomFields, ChatCustomEntity


class ChatCustomRepository(BaseRepository[ChatCustomManager, ChatCustomFields, ChatCustomEntity]):
    def __init__(self, manager: Optional[ChatCustomManager] = None):
        mapper = ChatCustomMapper()
        super().__init__(manager=manager or get_chat_custom_manager(), mapper=mapper)


def get_chat_custom_repository() -> ChatCustomRepository:
    return ChatCustomRepository()
