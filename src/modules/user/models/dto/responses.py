from pydantic import BaseModel, Field, model_validator
from typing import Optional
from typing_extensions import Self

from ..entities.user_entity import UserEntity


class SendCodeResponse(BaseModel):
    success: bool = Field()
    error_message: Optional[str] = Field(default=None)


class VerifyCodeResponse(BaseModel):
    success: bool = Field()
    token: Optional[str] = Field(default=None, description="JWT токен")
    user_uuid: Optional[str] = Field(default=None)
    user: Optional[UserEntity] = Field(default=None)
    error_message: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def check_success_consistency(self) -> Self:
        if self.success:
            if self.token is None:
                raise ValueError("Token must be provided when success is True")
            if self.user_uuid is None:
                raise ValueError("User UUID must be provided when success is True")
            if self.error_message is not None:
                raise ValueError("Error message must be None when success is True")
        else:
            if self.token is not None:
                raise ValueError("Token must be None when success is False")
            if self.user_uuid is not None:
                raise ValueError("User UUID must be None when success is False")
            if self.error_message is None:
                raise ValueError("Error message must be provided when success is False")
        return self
