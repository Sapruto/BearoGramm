from sqlalchemy.orm import InstrumentedAttribute
from src.general.db.base_manager import BaseManager

from src.modules.chats.chat_custom.models.orm.chat_custom_orm import ChatCustomORM


class ChatCustomManager(BaseManager[ChatCustomORM]):
    def __init__(self):
        super().__init__(ChatCustomORM, [ChatCustomORM.uuid])

    @property
    def identifier_field(self) -> InstrumentedAttribute:
        return ChatCustomORM.uuid


def get_chat_custom_manager() -> ChatCustomManager:
    return ChatCustomManager()
