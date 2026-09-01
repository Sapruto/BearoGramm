from typing import Optional
from sqlalchemy import select, exists

from src.modules.user import UserEntity
from ..repositories.chat_repository import ChatRepository, get_chat_repository
from ...models.entities.chat_entity import ChatEntity
from src.core.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    def __init__(self, chat_repository: Optional[ChatRepository] = None):
        self.chat_repository = chat_repository or get_chat_repository()

    async def chat_exists(self, chat_uuid: str) -> bool:
        try:
            chat = await self.chat_repository.get_by_id(chat_uuid)
            return chat is not None
        except Exception as e:
            logger.error(f"Error checking chat exists: {e}")
            return False

    async def user_in_chat(self, chat_uuid: str, user: UserEntity) -> bool:
        try:
            chat = await self.chat_repository.get_by_id(chat_uuid)
            if not chat:
                return False

            for access in chat.accesses:
                if hasattr(access, "user_uuid") and access.user_uuid == user.uuid:
                    return True
                if hasattr(access, "get_user_uuid"):
                    if access.get_user_uuid() == user.uuid:
                        return True

            return False

        except Exception as e:
            logger.error(f"Error checking user in chat: {e}")
            return False

    async def get_chat(self, chat_uuid: str) -> Optional[ChatEntity]:
        try:
            return await self.chat_repository.get_by_id(chat_uuid)
        except Exception as e:
            logger.error(f"Error getting chat: {e}")
            return None


def get_chat_service() -> ChatService:
    return ChatService()
