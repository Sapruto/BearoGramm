from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PersonalContact(BaseModel):
    chat_uuid: str
    user_uuid: str
    is_blocked: bool = False
    last_message_at: Optional[datetime] = None
    unread_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
