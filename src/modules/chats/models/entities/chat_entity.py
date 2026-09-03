from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List
from datetime import datetime

from ...chat_types.chat_types import ChatType


class ChatFields(str, Enum):
    UUID = "uuid"

    CHAT_TYPE = "chat_type"

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"

    def __str__(self):
        return self.value


class ChatEntity(BaseModel):
    uuid: Optional[str] = Field(default=None)

    chat_type: ChatType = Field(default=ChatType.DEFAULT)

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
