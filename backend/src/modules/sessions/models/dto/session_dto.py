from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SessionDTO(BaseModel):
    token: str
    user_uuid: str
    expired_at: Optional[datetime] = None


class CreateSessionDTO(BaseModel):
    user_uuid: str


class SessionResultDTO(BaseModel):
    token: str
    user_uuid: str
    expires_at: datetime
    expires_in_seconds: int
