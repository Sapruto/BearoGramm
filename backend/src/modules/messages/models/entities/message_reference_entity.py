from enum import Enum
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from ..enums.reference_type import ReferenceType


class MessageReferenceFields(str, Enum):
    UUID = "uuid"
    REFERENCE_TYPE = "reference_type"
    SOURCE_UUID = "source_uuid"
    TARGET_UUID = "target_uuid"
    SPAN_START = "span_start"
    SPAN_END = "span_end"
    SPAN_ALL = "span_all"
    CREATED_AT = "created_at"

    def __str__(self):
        return self.value


class MessageReferenceEntity(BaseModel):
    uuid: Optional[str] = Field(default=None)
    reference_type: ReferenceType
    source_uuid: Optional[str] = Field(default=None)
    target_uuid: Optional[str] = Field(default=None)
    span_start: Optional[int] = Field(default=None)
    span_end: Optional[int] = Field(default=None)
    span_all: Optional[bool] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)

    @field_serializer("created_at")
    def serialize_dt(self, v: datetime | None, _info):
        if v is None:
            return None
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
