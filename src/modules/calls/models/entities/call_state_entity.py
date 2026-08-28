from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
from datetime import datetime, timezone

class CallStateFields(str, Enum):
    USER_UUID = "user_uuid"
    ROOM_ID = "room_id"
    STATUS = "status"
    PARTICIPANTS = "participants"
    SDP_OFFER = "sdp_offer"
    SDP_ANSWER = "sdp_answer"
    CALLER_UUID = "caller_uuid"
    CALLEE_UUID = "callee_uuid"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    CALL_TYPE = "call_type"

    def __str__(self):
        return self.value

class CallStatus(str, Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    REJECTED = "rejected"
    ENDED = "ended"
    TIMEOUT = "timeout"

class CallType(str, Enum):
    P2P = "p2p"
    ROOM = "room"

class CallStateEntity(BaseModel):
    user_uuid: str
    room_id: Optional[str] = None
    call_type: CallType = CallType.P2P
    status: CallStatus = CallStatus.WAITING

    caller_uuid: Optional[str] = None
    callee_uuid: Optional[str] = None

    sdp_offer: Optional[str] = None
    sdp_answer: Optional[str] = None

    participants: List[str] = []

    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    @property
    def ttl(self) -> int:
        ttl_map = {
            CallStatus.WAITING: 30,
            CallStatus.ACTIVE: 3600,
            CallStatus.REJECTED: 300,
            CallStatus.ENDED: 86400,
            CallStatus.TIMEOUT: 60
        }

        ttl = ttl_map.get(self.status, 30)

        if self.call_type == CallType.ROOM and self.status == CallStatus.ACTIVE:
            ttl = 7200
        if self.room_id and self.status == CallStatus.ACTIVE:
            ttl = 7200

        return ttl

    def update_ttl(self, new_ttl: int) -> 'CallStateEntity':
        return self
