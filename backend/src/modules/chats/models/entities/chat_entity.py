from uuid import uuid4

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List
from datetime import datetime, timezone

from ...chat_types.chat_types import ChatType


class ChatFields(str, Enum):
    UUID = "uuid"

    CHAT_TYPE = "chat_type"

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"

    def __str__(self):
        return self.value


class ChatEntity(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid4()))

    chat_type: ChatType = Field(default=ChatType.DEFAULT)

    created_at: datetime = Field(default=datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
