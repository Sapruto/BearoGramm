from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class ProfileCustomResponse(BaseModel):
    uuid: str
    data: Dict[str, Any] = Field(default={})
    updated_at: Optional[datetime] = Field(default=None)
    user_uuid: Optional[str] = Field(default=None)


class CreateProfileResponse(BaseModel):
    success: bool = Field(default=False)
    message: str = Field(default="")
    profile: Optional[ProfileCustomResponse] = Field(default=None)


class GetProfileResponse(BaseModel):
    success: bool = Field(default=False)
    profile: Optional[ProfileCustomResponse] = Field(default=None)


class UpdateProfileResponse(BaseModel):
    success: bool = Field(default=False)
    message: str = Field(default="")
    profile: Optional[ProfileCustomResponse] = Field(default=None)


class DeleteProfileResponse(BaseModel):
    success: bool = Field(default=False)
    message: str = Field(default="")
