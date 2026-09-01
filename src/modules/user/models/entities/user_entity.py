from pydantic import BaseModel, Field
from enum import Enum

from typing import Optional
from datetime import datetime


class UserFields(str, Enum):
    UUID = "uuid"

    PHONE_NUMBER = "phone_number"
    PHONE_NUMBER_HASH = "phone_number_hash"
    PHONE_NUMBER_MASK = "phone_number_mask"

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"

    def __str__(self):
        return self.value


class UserEntity(BaseModel):
    uuid: Optional[str] = Field(default=None)

    phone_number: str = Field()

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
