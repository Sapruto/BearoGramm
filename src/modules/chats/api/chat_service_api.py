from typing import Optional, List

from src.core.logger import get_logger
from src.modules.user import UserEntity

from ..models.entities.chat_entity import ChatEntity
from ..core.services.chat_service import ChatService, get_chat_service


logger = get_logger(__name__)


class ChatServiceAPI:
    def __init__(self, chat_service: Optional[ChatService] = None):
        self._service = chat_service or get_chat_service()

    async def chat_exists(self, chat_uuid: str) -> bool:
        return await self._service.chat_exists(chat_uuid)

    async def user_in_chat(self, chat_uuid: str, user: UserEntity) -> bool:
        return await self._service.user_in_chat(chat_uuid, user)

    async def get_chat(self, chat_uuid: str) -> Optional[ChatEntity]:
        return await self._service.get_chat(chat_uuid)

    async def get_chat_by_uuid(self, chat_uuid: str) -> Optional[ChatEntity]:
        return await self._service.get_chat_by_uuid(chat_uuid)

    async def get_chats_by_user(self, user_uuid: str) -> List[ChatEntity]:
        return await self._service.get_chats_by_user(user_uuid)

    async def delete_chat(self, chat_uuid: str) -> bool:
        return await self._service.delete_chat(chat_uuid)

    async def get_chat_participants(self, chat_uuid: str) -> List[str]:
        return await self._service.get_chat_participants(chat_uuid)


def get_chat_service_api() -> ChatServiceAPI:
    return ChatServiceAPI()
