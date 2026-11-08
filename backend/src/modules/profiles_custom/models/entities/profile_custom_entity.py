from uuid import uuid4

from pydantic import BaseModel, Field, model_validator
from enum import Enum
from datetime import datetime, timezone
from typing import Optional

from ..enums import Gender
from src.modules.media.default_avatar_randomizer import get_avatar_randomizer


class ProfileCustomFields(str, Enum):
    UUID = "uuid"

    NAME = "name"
    AVATAR_UUID = "avatar_url"

    BANNER_COLOR = "banner_color"
    GENDER = "gender"
    BIO = "bio"

    UPDATED_AT = "updated_at"
    USER_UUID = "user_uuid"

    def __str__(self):
        return self.value


class ProfileCustomEntity(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid4()))

    name: str = Field(default="Unnamed")
    avatar_uuid: str = Field(default_factory=lambda: str(get_avatar_randomizer().get_random_avatar()))

    banner_color: str = Field(default="#000000")

    gender: Gender = Field(default=Gender.BEAR)
    bio: str = Field(default="I am ameba")

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_uuid: Optional[str] = Field(default=None)

    @model_validator(mode='after')
    def validate_hex(self) -> "ProfileCustomEntity":
        if not self.banner_color.startswith("#"):
            raise ValueError("Want to start with #")
        if len(self.banner_color) != 7:
            raise ValueError("Length is not correct")
        return self
