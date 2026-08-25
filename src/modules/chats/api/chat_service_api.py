from typing import Optional

from ..core.services.chat_service import ChatService, get_chat_service

class ChatServiceAPI:
    def __init__(self, service: Optional[ChatService] = None):
        self.service = service or get_chat_service()

    async def chat_exists(self, chat_uuid: str) -> bool:
        return await self.service.chat_exists(chat_uuid)

    async def user_in_chat(self, chat_uuid: str, user) -> bool:
        return await self.service.user_in_chat(chat_uuid, user)

    async def get_chat(self, chat_uuid: str):
        return await self.service.get_chat(chat_uuid)

def get_chat_service_api() -> ChatServiceAPI:
    return ChatServiceAPI()
