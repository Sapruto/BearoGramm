from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserAPIModel(BaseModel):
    uuid: str
    phone_number: str
    phone_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserSessionsAPIModel(BaseModel):
    token: str
    user_uuid: str
    expires_at: Optional[datetime] = None

class UserSessionResponseAPIModel(BaseModel):
    user_uuid: str
    sessions: list[UserSessionsAPIModel]
    total: int
