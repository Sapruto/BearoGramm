from uuid import uuid4

from pydantic import BaseModel, Field, field_serializer, model_validator
from enum import Enum
from datetime import datetime
from typing import Any, Optional, Dict

from src.core.settings import Settings
from ..enums import Gender
from ..orm.default_avatar_randomizer import AvatarRandomizer


randomizer = AvatarRandomizer()


class ProfileCustomFields(str, Enum):
    UUID = "uuid"

    NAME = "name"
    AVATAR_URL = "avatar_url"

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
    avatar_url: str = Field(default_factory=lambda: str(randomizer.get_random_avatar()))

    banner_color: str = Field(default="#000000")

    gender: Gender = Field(default=Gender.BEAR)
    bio: str = Field(default="I am ameba")

    updated_at: Optional[datetime] = Field(default=None)
    user_uuid: Optional[str] = Field(default=None)

    # @model_validator(mode='before')
    # def validate_hex(self) -> None:
    #     if not self.banner_color.startswith("#"):
    #         raise ValueError("Want to start with #")
    #     if len(self.banner_color) != 7:
    #         raise ValueError("Length is not correct")

    @field_serializer('avatar_url')
    def serialize_avatar_url(self, avatar_url: Optional[str]) -> Optional[str]:
        if not avatar_url:
            return None
        return f"{Settings.MEDIA_BASE_URL.rstrip('/')}/{avatar_url.lstrip('/')}"
