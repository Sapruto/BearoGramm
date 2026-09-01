from sqlalchemy.orm import InstrumentedAttribute
from src.general.db.base_manager import BaseManager

from ...models.orm.message_orm import MessageORM


class MessageManager(BaseManager[MessageORM]):
    def __init__(self):
        super().__init__(MessageORM, [MessageORM.uuid, MessageORM.created_at])

    def identifier_field(self) -> InstrumentedAttribute:
        return MessageORM.uuid


def get_message_manager() -> MessageManager:
    return MessageManager()
