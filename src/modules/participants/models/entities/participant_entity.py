from pydantic import BaseModel, Field
from uuid import uuid4
from enum import Enum
from typing import Dict, Optional
from datetime import datetime

from ..enums import ResourceType,


class ParticipantFields(str, Enum):
    UUID = "uuid"
    USER_UUID = "user_uuid"
    RESOURCE_UUID = "resource_uuid"
    RESOURCE_TYPE = "resource_type"
    PERMISSIONS = "permissions"

    def __str__(self):
        return self.value


class ParticipantEntity(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    user_uuid: str
    resource_uuid: str
    resource_type: ResourceType
    permissions: Dict[str, bool] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"use_enum_values": True, "frozen": False, "extra": "forbid"}

    def has_permission(self, action: Enum) -> bool:
        return self.permissions.get(action.value, False)
