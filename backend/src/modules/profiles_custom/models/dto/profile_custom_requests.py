from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, Field
from ..enums import Gender


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(default=None)
    avatar_media: Optional[UploadFile] = Field(default=None)
    banner_color: Optional[str] = Field(default=None)
    gender: Optional[Gender] = Field(default=None)
    bio: Optional[str] = Field(default=None)

    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
