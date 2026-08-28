from typing import Optional, List
from sqlalchemy import select

from ..core.repositories.chat_repository import ChatRepository, get_chat_repository
from ..models.entities.chat_entity import ChatEntity, ChatFields
from ..models.orm.chat_orm import ChatORM
from ..models.message_action_type import MessageActionType

from src.general.repository.sql.sql_query import SqlQuery
from src.core.logger import get_logger

logger = get_logger(__name__)

class ChatServiceAPI:
    def __init__(self, chat_repository: Optional[ChatRepository] = None):
        self.chat_repository = chat_repository or get_chat_repository()

    async def chat_exists(self, chat_uuid: str) -> bool:
        try:
            query = SqlQuery[ChatFields]()
            query.add_filter(ChatFields.UUID, chat_uuid)
            chat = await self.chat_repository.get(query)
            return chat is not None
        except Exception as e:
            logger.error(f"Error checking chat exists: {e}")
            return False

    async def user_in_chat(self, chat_uuid: str, user_uuid: str, action_type: MessageActionType) -> bool:
        try:
            chat = await self.get_chat(chat_uuid)
            if not chat:
                return False

            for access in chat.accesses:
                if hasattr(access, 'user_uuid') and access.user_uuid == user_uuid:
                    return True
                if hasattr(access, 'get_user_uuid'):
                    if access.get_user_uuid() == user_uuid:
                        return True

            return False

        except Exception as e:
            logger.error(f"Error checking user in chat: {e}")
            return False

    async def get_chat(self, chat_uuid: str) -> Optional[ChatEntity]:
        try:
            query = SqlQuery[ChatFields]()
            query.add_filter(ChatFields.UUID, chat_uuid)
            return await self.chat_repository.get(query)
        except Exception as e:
            logger.error(f"Error getting chat: {e}")
            return None

    async def get_chat_by_uuid(self, chat_uuid: str) -> Optional[ChatEntity]:
        return await self.get_chat(chat_uuid)

    async def get_chats_by_user(self, user_uuid: str) -> list[ChatEntity]:
        try:
            stmt = select(ChatORM).where(
                ChatORM.accesses.contains([{"user_uuid": user_uuid}])
            )

            results = await self.chat_repository.manager.get_all_by_stmt(stmt)
            return [self.chat_repository._to_entity(r) for r in results]
        except Exception as e:
            logger.error(f"Error getting chats for user: {e}")
            return []

    async def delete_chat(self, chat_uuid: str) -> bool:
        try:
            query = SqlQuery[ChatFields]()
            query.add_filter(ChatFields.UUID, chat_uuid)
            deleted_count = await self.chat_repository.delete(query)
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting chat: {e}")
            return False

    async def get_chat_participants(self, chat_uuid: str) -> List[str]:
        try:
            chat = await self.get_chat(chat_uuid)
            if not chat:
                logger.warning(f"Chat {chat_uuid} not found")
                return []

            participants = []
            for access in chat.accesses:
                if hasattr(access, 'user_uuid'):
                    participants.append(access.user_uuid)
                elif hasattr(access, 'get_user_uuid'):
                    participants.append(access.get_user_uuid())

            return participants

        except Exception as e:
            logger.error(f"Error getting chat participants: {e}")
            return []

def get_chat_service_api() -> ChatServiceAPI:
    return ChatServiceAPI()
