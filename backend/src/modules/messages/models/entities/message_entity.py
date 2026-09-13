from pydantic import BaseModel, Field, SerializeAsAny, field_serializer
from enum import Enum

from datetime import datetime, timezone
from typing import List, Optional

from src.general.processors.base.base_data import BaseData, base_data_type


class MessageFields(str, Enum):
    UUID = "uuid"
    MESSAGE_DATA = "message_data"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    CHAT_UUID = "chat_uuid"
    USER_UUID = "user_uuid"

    def __str__(self):
        return self.value


class MessageEntity(BaseModel):
    uuid: Optional[str] = Field(default=None)

    message_data: List[SerializeAsAny[BaseData]] = Field(default_factory=list)

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    chat_uuid: Optional[str] = Field(default=None)
    user_uuid: Optional[str] = Field(default=None)

    def add_content(self, new_data: base_data_type) -> None:
        self.message_data.append(new_data)

    def remove_content(self, delete_data: base_data_type) -> None:
        if delete_data in self.message_data:
            self.message_data.remove(delete_data)

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, v: datetime | None, _info):
        if v is None:
            return None
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
