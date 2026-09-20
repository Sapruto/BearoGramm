from pydantic import BaseModel, Field
from typing import List, Optional

from ..entities.message_entity import MessageEntity


class SendMessageResponse(BaseModel):
    success: bool = True
    message_entity: Optional[MessageEntity] = None


class UpdateMessageResponse(BaseModel):
    success: bool = True
    message_entity: Optional[MessageEntity] = None


class DeleteMessageResponse(BaseModel):
    success: bool = True


class GetMessagesResponse(BaseModel):
    success: bool = True
    message_entity: List[MessageEntity] = Field(default_factory=list)
