from sqlalchemy.orm import InstrumentedAttribute

from src.general.db.base_manager import BaseManager

from ...models.orm.message_reference_orm import MessageReferenceORM


class MessageReferenceManager(BaseManager[MessageReferenceORM]):
    def __init__(self):
        super().__init__(
            MessageReferenceORM,
            [MessageReferenceORM.uuid, MessageReferenceORM.created_at],
        )

    @property
    def identifier_field(self) -> InstrumentedAttribute:
        return MessageReferenceORM.uuid


def get_message_reference_manager() -> MessageReferenceManager:
    return MessageReferenceManager()
