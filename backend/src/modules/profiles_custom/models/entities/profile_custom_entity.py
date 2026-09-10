from pydantic import BaseModel, Field
from enum import Enum

from datetime import datetime
from typing import Optional, Dict

from src.core.paths import DefaultAvatarPath
from src.general.processors.base.base_data import base_data_type


class ProfileCustomFields(str, Enum):
    UUID = "uuid"

    NAME = "name"
    AVATAR_URL = "avatar_url"

    DATA = "data"
    UPDATED_AT = "updated_at"
    USER_UUID = "user_uuid"

    def __str__(self):
        return self.value


class ProfileCustomEntity(BaseModel):
    uuid: Optional[str] = Field(default=None)

    name: str = Field(default="Unified")
    avatar_url: str = Field(default=DefaultAvatarPath)

    data: Dict[str, base_data_type] = Field(default={})
    updated_at: Optional[datetime] = Field(default=None)
    user_uuid: Optional[str] = Field(default=None)
