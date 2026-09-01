from abc import ABC, abstractmethod
from typing import TypeVar, Optional, List
from pydantic import BaseModel

from src.modules.participants import Permission
from ...core.repositories.chat_repository import ChatRepository, get_chat_repository


BaseResponseType = TypeVar("BaseResponseType", bound=BaseModel)


class BaseChatService(ABC):
    def __init__(self, repository: Optional[ChatRepository] = None):
        self.repository = repository or get_chat_repository()

    @abstractmethod
    async def create_personal_chat(
        self, user_uuid: str, companion_uuid: str
    ) -> BaseResponseType:
        pass

    @abstractmethod
    async def get_chat(
        self, chat_uuid: str, user_uuid: str
    ) -> BaseResponseType:
        pass

    @abstractmethod
    async def get_chats_for_user(
        self, user_uuid: str, limit: int = 50, offset: int = 0
    ) -> BaseResponseType:
        pass

    @abstractmethod
    async def get_contact_list(
        self, user_uuid: str, limit: int = 50, offset: int = 0
    ) -> BaseResponseType:
        pass

    @abstractmethod
    async def add_permissions(
        self, chat_uuid: str, from_user_uuid: str, to_user_uuid: str, permissions: List[Permission]
    ) -> BaseResponseType:
        pass

    @abstractmethod
    async def remove_permissions(
        self, chat_uuid: str, from_user_uuid: str, to_user_uuid: str, permissions: List[Permission]
    ) -> BaseResponseType:
        pass

    @abstractmethod
    async def delete_chat(self, chat_uuid: str, user_uuid: str) -> BaseResponseType:
        pass
