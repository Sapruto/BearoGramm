from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserSessionsAPIModel(BaseModel):
    token: str
    user_uuid: str
    expires_at: Optional[datetime] = None


class UserSessionResponseAPIModel(BaseModel):
    user_uuid: str
    sessions: list[UserSessionsAPIModel]
    total: int
