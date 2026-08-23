from pydantic import BaseModel
from typing import Optional, List

from src.modules.chats.models.entities.chat_entity import ChatEntity
from src.modules.chats.chat_types.personal.models.personal_contact import PersonalContact

class CreateChatResponse(BaseModel):
    chat: ChatEntity

class GetChatResponse(BaseModel):
    chat: ChatEntity

class ListChatsResponse(BaseModel):
    chats: List[ChatEntity]
    total: int

class ContactsResponse(BaseModel):
    contacts: List[PersonalContact]
    total: int

class FindChatResponse(BaseModel):
    chat: Optional[ChatEntity] = None
    found: bool = False

class BlockUserResponse(BaseModel):
    chat: ChatEntity

class UnblockUserResponse(BaseModel):
    chat: ChatEntity

class DeleteChatResponse(BaseModel):
    chat_uuid: str

class ErrorResponse(BaseModel):
    detail: str
    status_code: int
