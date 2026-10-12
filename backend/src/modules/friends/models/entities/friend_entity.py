from pydantic import BaseModel, Field, model_validator
from enum import Enum

from datetime import datetime, timezone
from uuid import uuid4

from ..enums import FriendStatus


class FriendFields(str, Enum):
    UUID = "uuid"

    USER_UUID1 = "user_uuid1"
    USER_STATUS1 = "user_status1"

    USER_UUID2 = "user_uuid2"
    USER_STATUS2 = "user_status2"

    INITIATOR_UUID = "initiator_uuid"

    CREATED_AT = "created_at"

    def __str__(self):
        return self.value


class FriendEntity(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid4()))

    user_uuid1: str = Field()
    user_status1: FriendStatus = Field(default=FriendStatus.PROCESS)

    user_uuid2: str = Field()
    user_status2: FriendStatus = Field(default=FriendStatus.PROCESS)

    initiator_uuid: str = Field()

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_initiator_uuid(self):
        if self.initiator_uuid != self.user_uuid1 and self.initiator_uuid != self.user_uuid2:
            raise ValueError("initiator_uuid must be first or second user_uuid")
