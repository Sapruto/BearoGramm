from pydantic import BaseModel, Field
from typing import List, Tuple, Any, Optional


class CreateProfileRequest(BaseModel):
    typing_to_data: List[Tuple[str, Any]] = Field(default=[])
    user_uuid: Optional[str] = Field(default=None)
    profile_uuid: Optional[str] = Field(default=None)


class UpdateProfileRequest(BaseModel):
    typing_to_data: List[Tuple[str, Any]] = Field(default=[])