from pydantic import BaseModel, Field
from typing import Optional, List

from ..entities.message_entity import MessageEntity

class SendMessageResponse(BaseModel):
    success: bool = Field(...)
    message_entity: Optional[MessageEntity] = Field(default=None)
    error_message: Optional[str] = Field(default=None)

class GetMessagesResponse(BaseModel):
    success: bool = Field(...)
    message_entity: Optional[List[MessageEntity]] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
