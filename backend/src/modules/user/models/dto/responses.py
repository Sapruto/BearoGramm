from pydantic import BaseModel, Field
from typing import Optional

from src.modules.profiles_custom.models.entities.profile_custom_entity import ProfileCustomEntity
from ..entities.user_entity import UserEntity


class SendCodeResponse(BaseModel):
    success: bool = Field(default=True)


class VerifyCodeResponse(BaseModel):
    token: str = Field(description="JWT токен")
    user_uuid: str = Field()
    user: UserEntity = Field()
    just_created_profile: bool = Field(default=False)
    just_created: bool = Field(default=False)
    profile: Optional[ProfileCustomEntity] = Field(default=None)
