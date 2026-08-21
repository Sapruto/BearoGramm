from pydantic import BaseModel, model_validator, Field
from typing import Optional
from typing_extensions import Self

from ..entities.user_entity import UserEntity

class SendCodeResponse(BaseModel):
    success: bool = Field()
    error_message: Optional[str] = Field(default=None)

class VerifyCodeResponse(BaseModel):
    success: bool = Field()
    user: Optional[UserEntity] = Field(default=None)
    error_message: Optional[str] = Field(default=None)

    @model_validator(mode='after')
    def check_success_consistency(self) -> Self:
        if self.success:
            if self.user is None:
                raise ValueError('User must be provided when success is True')
            if self.error_message is not None:
                raise ValueError('Error message must be None when success is True')
        else:
            if self.user is not None:
                raise ValueError('User must be None when success is False')
            if self.error_message is None:
                raise ValueError('Error message must be provided when success is False')
        return self
