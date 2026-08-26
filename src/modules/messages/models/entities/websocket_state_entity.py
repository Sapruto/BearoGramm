from pydantic import BaseModel, Field
from enum import Enum

class WebSocketStateFields(Enum):
    USER_UUID = "user_uuid"
    ONLINE = "online"
    LAST_ACTIVE = "last_active"

class WebSocketStateEntity(BaseModel):
    user_uuid: str = Field(...)
    online: bool = Field(...)
    last_activity: bool = Field(...)
