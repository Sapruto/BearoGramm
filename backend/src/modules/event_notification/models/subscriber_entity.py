from pydantic import BaseModel, Field
from enum import Enum


class SubscriberFields(str, Enum):
    UUID = "uuid"

    def __str__(self):
        return self.value


class SubscriberEntity(BaseModel):
    uuid: str = Field(...)
