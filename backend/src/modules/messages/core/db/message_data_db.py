from sqlalchemy.orm import InstrumentedAttribute

from src.general.db.base_manager import BaseManager

from ...models.orm.message_data_orm import MessageDataORM


class MessageDataManager(BaseManager[MessageDataORM]):
    def __init__(self):
        super().__init__(
            MessageDataORM,
            [MessageDataORM.message_uuid, MessageDataORM.extra_data_type],
        )

    @property
    def identifier_field(self) -> InstrumentedAttribute:
        return MessageDataORM.message_uuid


def get_message_data_manager() -> MessageDataManager:
    return MessageDataManager()
