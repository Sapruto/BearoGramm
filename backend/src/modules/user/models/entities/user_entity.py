from uuid import uuid4

from pydantic import BaseModel, Field
from enum import Enum

from typing import Optional
from datetime import datetime, timezone


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
    uuid: str = Field(default_factory=lambda: str(uuid4()))

    phone_number: str = Field()

    created_at: datetime = Field(default=datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
