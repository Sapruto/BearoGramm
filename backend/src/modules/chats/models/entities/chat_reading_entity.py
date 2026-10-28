from uuid import uuid4

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime, timezone


class ChatReadingFields(str, Enum):
    UUID = "uuid"

    CHAT_UUID = "chat_uuid"
    USER_UUID = "user_uuid"

    LAST_READ_MESSAGE_UUID = "last_read_message_uuid"

    UPDATED_AT = "updated_at"

    def __str__(self):
        return self.value


class ChatReadingEntity(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid4()))

    chat_uuid: str
    user_uuid: str

    last_read_message_uuid: Optional[str] = Field(default=None)

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
