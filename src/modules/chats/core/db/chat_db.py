from sqlalchemy.orm import InstrumentedAttribute
from src.general.db.base_manager import BaseManager

from ...models.orm.chat_orm import ChatORM


class ChatManager(BaseManager[ChatORM]):
    def __init__(self):
        super().__init__(
            ChatORM, [ChatORM.uuid, ChatORM.access_type, ChatORM.created_at]
        )

    def identifier_field(self) -> InstrumentedAttribute:
        return ChatORM.uuid


def get_chat_manager() -> ChatManager:
    return ChatManager()
