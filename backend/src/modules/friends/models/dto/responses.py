from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

from src.modules.profiles_custom import ProfileCustomEntity
from ..enums import FriendStatus


class FriendItemResponse(BaseModel):
    user_uuid: str
    status: FriendStatus
    is_initiator: bool
    created_at: datetime
    profile: ProfileCustomEntity = ProfileCustomEntity()


class FriendRequestResponse(BaseModel):
    from_user_uuid: str
    to_user_uuid: str
    status: FriendStatus
    created_at: datetime


class GetFriendsResponse(BaseModel):
    items: List[FriendItemResponse]
    total: int


class GetFriendRequestsResponse(BaseModel):
    incoming: List[FriendRequestResponse]
    outgoing: List[FriendRequestResponse]
    total_incoming: int
    total_outgoing: int


class FriendActionResponse(BaseModel):
    success: bool
    just_created_chat: bool = False
    uuid: Optional[str] = None
    other_uuid: Optional[str] = None
    message: Optional[str] = None
