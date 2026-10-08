from pydantic import BaseModel
from enum import Enum

from ..enums import FriendStatus


class TargetIdentifier(str, Enum):
    UUID = "uuid"
    USERNAME = "username"
    EMAIL = "email"
    PHONE = "phone"


class SendFriendRequest(BaseModel):
    target_value: str
    target_type: TargetIdentifier


class FriendStatusRequest(BaseModel):
    target_uuid: str
    status: FriendStatus
