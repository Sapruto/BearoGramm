from pydantic import BaseModel
from typing import Optional, List

from src.modules.chats.models.entities.chat_entity import ChatEntity
from src.modules.chats.chat_types.personal.models.personal_contact import PersonalContact

class CreateChatResponse(BaseModel):
    success: bool
    chat: Optional[ChatEntity] = None
    error_message: Optional[str] = None

class GetChatResponse(BaseModel):
    success: bool
    chat: Optional[ChatEntity] = None
    error_message: Optional[str] = None

class ListChatsResponse(BaseModel):
    success: bool
    chats: Optional[List[ChatEntity]] = None
    total: Optional[int] = None
    error_message: Optional[str] = None

class ContactsResponse(BaseModel):
    success: bool
    contacts: Optional[List[PersonalContact]] = None
    total: Optional[int] = None
    error_message: Optional[str] = None

class FindChatResponse(BaseModel):
    chat: Optional[ChatEntity] = None
    found: bool = False

class BlockUserResponse(BaseModel):
    success: bool
    chat: Optional[ChatEntity] = None
    error_message: Optional[str] = None

class UnblockUserResponse(BaseModel):
    success: bool
    chat: Optional[ChatEntity] = None
    error_message: Optional[str] = None

class DeleteChatResponse(BaseModel):
    success: bool
    error_message: Optional[str] = None
