from pydantic import BaseModel, Field
from enum import Enum

from typing import Optional
from datetime import datetime, timezone

from .enums import MediaType


class MediaFields(str, Enum):
    UUID = "uuid"
    FULL_URL = "full_url"
    URL = "url"
    HASH = "hash"
    FILENAME = "filename"
    CONTENT_TYPE = "content_type"
    MEDIA_TYPE = "media_type"
    SIZE = "size"
    VERSION = "version"
    PTRS = "ptrs"
    CREATED_AT = "created_at"

    def __str__(self):
        return self.value


class MediaEntity(BaseModel):
    uuid: Optional[str] = Field(default=None)

    full_url: str = Field()
    url: str = Field()
    hash: str = Field()
    filename: str = Field()
    content_type: str = Field()
    media_type: MediaType = Field(default=MediaType.ATTACHMENT)
    size: int = Field()
    version: int = Field(default=1)

    ptrs: int = Field(default=1)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
