from pydantic import BaseModel, Field, field_validator
from enum import Enum

from datetime import datetime
from typing import List, Optional, Any

from ...types.base.base_message_data import base_message_data_type

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

    message_data: List[base_message_data_type] = Field(default=[])

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    chat_uuid: Optional[str] = Field(default=None)
    user_uuid: Optional[str] = Field(default=None)

    @field_validator('message_data')
    @classmethod
    def validate_message_data(cls, v: Any) -> List[base_message_data_type]:
        if not v:
            return []

        if not isinstance(v, list):
            raise ValueError("accesses must be a list")

        for current_message_data in v:
            if not hasattr(current_message_data, 'get_type'):
                raise ValueError(f"Invalid access type: {current_message_data}")

        return v

    def add_content(self, new_data: base_message_data_type) -> None:
        self.message_data.append(new_data)

    def remove_content(self, delete_data: base_message_data_type) -> None:
        if delete_data in self.message_data:
            self.message_data.remove(delete_data)
