from pydantic import BaseModel, Field, field_serializer
from enum import Enum
from datetime import datetime, timezone
from typing import List, Optional

from .message_data_entity import MessageDataEntity
from .message_reference_entity import MessageReferenceEntity


class MessageFields(str, Enum):
    UUID = "uuid"
    MESSAGE_TEXT = "message_text"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    HAS_EXTRA_DATA = "has_extra_data"
    CHAT_UUID = "chat_uuid"
    USER_UUID = "user_uuid"
    EXTRA_DATA = "extra_data"
    REFERENCES = "references"

    def __str__(self):
        return self.value


class MessageEntity(BaseModel):
    uuid: Optional[str] = Field(default=None)
    message_text: Optional[str] = Field(default=None)

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    has_extra_data: bool = Field(default=False)

    chat_uuid: Optional[str] = Field(default=None)
    user_uuid: Optional[str] = Field(default=None)

    extra_data: Optional[MessageDataEntity] = Field(default=None)
    references: List[MessageReferenceEntity] = Field(default_factory=list)

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, v: datetime | None, _info):
        if v is None:
            return None
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
