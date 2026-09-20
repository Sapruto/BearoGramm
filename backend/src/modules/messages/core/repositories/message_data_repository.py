from typing import Optional

from src.general.repository.sql.sql_base_repository import BaseRepository

from .mappers.message_data_mapper import MessageDataMapper
from ..db.message_data_db import MessageDataManager, get_message_data_manager
from ...models.entities.message_data_entity import (
    MessageDataFields,
    MessageDataEntity,
)


class MessageDataRepository(
    BaseRepository[MessageDataManager, MessageDataFields, MessageDataEntity]
):
    def __init__(self, manager: Optional[MessageDataManager] = None):
        mapper = MessageDataMapper()
        super().__init__(manager=manager or get_message_data_manager(), mapper=mapper)


def get_message_data_repository() -> MessageDataRepository:
    return MessageDataRepository()
