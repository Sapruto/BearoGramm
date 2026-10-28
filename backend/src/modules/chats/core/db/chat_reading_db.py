from sqlalchemy.orm import InstrumentedAttribute
from src.general.db.base_manager import BaseManager

from ...models.orm.chat_reading_orm import ChatReadingORM


class ChatReadingManager(BaseManager[ChatReadingORM]):
    def __init__(self):
        super().__init__(
            ChatReadingORM, [ChatReadingORM.uuid, ChatReadingORM.created_at]
        )

    @property
    def identifier_field(self) -> InstrumentedAttribute:
        return ChatReadingORM.uuid


def get_chat_reading_manager() -> ChatReadingManager:
    return ChatReadingManager()
