from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class CreateSessionRequest(BaseModel):
    user_uuid: str


class CreateSessionResponse(BaseModel):
    token: str
    user_uuid: str
    expires_at: datetime
    expires_in_seconds: int


class ValidateSessionResponse(BaseModel):
    is_valid: bool
    user_uuid: Optional[str] = None
    expired_at: Optional[datetime] = None


class RefreshSessionResponse(BaseModel):
    token: str
    user_uuid: str
    expires_at: datetime
    expires_in_seconds: int


class DeleteSessionResponse(BaseModel):
    success: bool


class SessionInfoResponse(BaseModel):
    token: str
    user_uuid: str
    expired_at: Optional[datetime] = None


class UserSessionsResponse(BaseModel):
    user_uuid: str
    sessions: list[SessionInfoResponse]
    total: int
