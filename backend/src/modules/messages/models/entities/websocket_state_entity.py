from pydantic import BaseModel, Field
from enum import Enum


class WebSocketStateFields(Enum):
    USER_UUID = "user_uuid"
    ONLINE = "online"

    def __str__(self):
        return self.value


class WebSocketStateEntity(BaseModel):
    user_uuid: str = Field(...)
    online: bool = Field(default=True)
