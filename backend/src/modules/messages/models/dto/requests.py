from pydantic import BaseModel, Field
from typing import List, Optional

from ..entities.message_data_entity import MessageDataEntity
from ..entities.message_reference_entity import MessageReferenceEntity


class SendMessageRequest(BaseModel):
    chat_uuid: str
    message_text: Optional[str] = None
    extra_data: Optional[MessageDataEntity] = None
    references: List[MessageReferenceEntity] = Field(default_factory=list)


class UpdateMessageRequest(BaseModel):
    message_uuid: str
    message_text: Optional[str] = None
    extra_data: Optional[MessageDataEntity] = None
    clear_extra_data: bool = False
