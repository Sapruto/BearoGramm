from typing import Optional

from src.general.repository.sql.sql_base_repository import BaseRepository

from .mappers.message_reference_mapper import MessageReferenceMapper
from ..db.message_reference_db import (
    MessageReferenceManager,
    get_message_reference_manager,
)
from ...models.entities.message_reference_entity import (
    MessageReferenceFields,
    MessageReferenceEntity,
)


class MessageReferenceRepository(
    BaseRepository[
        MessageReferenceManager, MessageReferenceFields, MessageReferenceEntity
    ]
):
    def __init__(self, manager: Optional[MessageReferenceManager] = None):
        mapper = MessageReferenceMapper()
        super().__init__(
            manager=manager or get_message_reference_manager(), mapper=mapper
        )


def get_message_reference_repository() -> MessageReferenceRepository:
    return MessageReferenceRepository()
