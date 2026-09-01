from typing import Any, Optional
from datetime import datetime

from ...base.base_access_type import BaseAccessType
from .personal_access_threshold import PersonalAccessThreshold

PERSONAL_TYPE = "personal"


class PersonalAccessType(BaseAccessType[PersonalAccessThreshold]):
    is_blocked: bool = False
    blocked_at: Optional[datetime] = None
    blocked_by: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0

    def get_threshold(self) -> PersonalAccessThreshold:
        return PersonalAccessThreshold(
            is_blocked=self.is_blocked,
            blocked_at=self.blocked_at,
            blocked_by=self.blocked_by,
            last_message_at=self.last_message_at,
            unread_count=self.unread_count,
        )

    def get_raw_data(self) -> Any:
        return {
            "user_uuid": self.user_uuid,
            "is_blocked": self.is_blocked,
            "blocked_at": self.blocked_at.isoformat() if self.blocked_at else None,
            "blocked_by": self.blocked_by,
            "last_message_at": self.last_message_at.isoformat()
            if self.last_message_at
            else None,
            "unread_count": self.unread_count,
        }

    def get_type(self) -> str:
        return PERSONAL_TYPE

    @classmethod
    def create_from_user_uuid(cls, user_uuid: str) -> "PersonalAccessType":
        return cls(user_uuid=user_uuid, is_blocked=False, unread_count=0)
