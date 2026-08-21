from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class SessionFields(str, Enum):
    USER_UUID = "user_uuid"
    TOKEN = "token"
    EXPIRED_AT = "expired_at"

    def __str__(self):
        return self.value

class SessionEntity(BaseModel):
    user_uuid: str
    token: Optional[str]
    expired_at: Optional[datetime]
