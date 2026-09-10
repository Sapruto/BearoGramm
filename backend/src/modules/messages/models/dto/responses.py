from pydantic import BaseModel, Field
from typing import Optional, List

from ..entities.message_entity import MessageEntity


class SendMessageResponse(BaseModel):
    success: bool = Field(default=True)
    message_entity: Optional[MessageEntity] = Field(default=None)


class UpdateMessageResponse(BaseModel):
    success: bool = Field(default=True)
    message_entity: Optional[MessageEntity] = Field(default=None)


class DeleteMessageResponse(BaseModel):
    success: bool = Field(default=True)


class GetMessagesResponse(BaseModel):
    success: bool = Field(default=True)
    message_entity: Optional[List[MessageEntity]] = Field(default=None)
