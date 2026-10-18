from enum import Enum
from random import choice
from typing import Generic, TypeVar

from pydantic import BaseModel, Field


ExceptionType = TypeVar("ExceptionType", bound=Enum)
_DEFAULT_MESSAGES = ("F*ck your mother!", "You are ameba!")


class DetailHTTPError(BaseModel, Generic[ExceptionType]):
    error_message: str = Field(default="", max_length=255)
    exception_type: ExceptionType = Field(...)
    friendly_message: str = Field(default_factory=lambda: choice(_DEFAULT_MESSAGES), max_length=255)
