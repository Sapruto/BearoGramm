from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class MediaUploadRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=512)
    content_type: Optional[str] = Field(default=None, max_length=255)
    content: bytes


class MediaDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    filename: str
    url: str
    content_type: Optional[str] = None
    size: int
    uploaded_at: datetime


class MediaUploadResponse(BaseModel):
    success: bool
    media: Optional[MediaDTO] = None
    error: Optional[str] = None


class MediaDeleteResponse(BaseModel):
    success: bool
    filename: str
    error: Optional[str] = None


class MediaExistsResponse(BaseModel):
    exists: bool
    filename: str


class MediaMeta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    filename: str
    storage_key: str
    url: str
    content_type: Optional[str] = None
    size: int = 0
    uploaded_at: datetime = Field(default=datetime.now(timezone.utc))
