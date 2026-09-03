from pydantic import BaseModel, Field, model_validator
from typing import Optional
from typing_extensions import Self

from ..entities.user_entity import UserEntity


class SendCodeResponse(BaseModel):
    success: bool = Field(default=True)


class VerifyCodeResponse(BaseModel):
    token: str = Field(description="JWT токен")
    user_uuid: str = Field()
    user: UserEntity = Field()
