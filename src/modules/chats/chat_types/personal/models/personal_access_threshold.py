from datetime import datetime
from typing import Optional

from ...base.base_access_threshold import BaseAccessThreshold


class PersonalAccessThreshold(BaseAccessThreshold):
    is_blocked: bool = False
    blocked_at: Optional[datetime] = None
    blocked_by: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0

    def block(self, blocked_by: str) -> None:
        self.is_blocked = True
        self.blocked_at = datetime.now()
        self.blocked_by = blocked_by

    def unblock(self) -> None:
        self.is_blocked = False
        self.blocked_at = None
        self.blocked_by = None
