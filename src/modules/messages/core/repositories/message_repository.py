from src.general.repository.sql.sql_base_repository import BaseRepository
from typing import Optional

from .mappers.message_mapper import MessageMapper
from ..db.message_db import MessageManager, get_message_manager
from ...models.entities.message_entity import MessageFields, MessageEntity

class MessageRepository(BaseRepository[MessageManager, MessageFields, MessageEntity]):
    def __init__(self, manager: Optional[MessageManager] = None):
        mapper = MessageMapper()
        super().__init__(manager=manager or get_message_manager(), mapper=mapper)

def get_message_repository() -> MessageRepository:
    return MessageRepository()
