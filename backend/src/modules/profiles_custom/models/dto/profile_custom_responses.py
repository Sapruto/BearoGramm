from typing import Optional
from pydantic import BaseModel, Field

from ..entities.profile_custom_entity import ProfileCustomEntity


class GetProfileResponse(BaseModel):
    success: bool = Field(default=False)
    profile: Optional[ProfileCustomEntity] = Field(default=None)


class UpdateProfileResponse(BaseModel):
    success: bool = Field(default=False)
    message: str = Field(default="")
    profile: Optional[ProfileCustomEntity] = Field(default=None)


class DeleteProfileResponse(BaseModel):
    success: bool = Field(default=False)
    message: str = Field(default="")
