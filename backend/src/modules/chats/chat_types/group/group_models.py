from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.modules.profiles_custom import ProfileCustomEntity
from ..chat_types import ChatType


class GroupParticipantResponse(BaseModel):
    user_uuid: str
    profile: Optional[ProfileCustomEntity] = None
    is_owner: bool = False


class GroupChatResponse(BaseModel):
    uuid: str
    chat_type: str = ChatType.GROUP
    name: str
    owner_uuid: str
    created_at: datetime
    updated_at: datetime
    participants: List[GroupParticipantResponse] = Field(default_factory=list)


class GroupChatPreview(BaseModel):
    uuid: str
    chat_type: str = ChatType.GROUP
    name: str
    owner_uuid: str
    participants_count: int
    last_message_preview: Optional[str] = None
    updated_at: datetime


class GroupChatCreateRequest(BaseModel):
    name: str
    participant_phones: List[str] = Field(default_factory=list)


class GroupChatListResponse(BaseModel):
    items: List[GroupChatPreview]
    total: int
    limit: int
    offset: int


class AddParticipantsRequest(BaseModel):
    phones: List[str]


class RemoveParticipantRequest(BaseModel):
    user_uuid: str


class RenameGroupRequest(BaseModel):
    name: str


class GroupActionResponse(BaseModel):
    message: str
    chat_uuid: str
    affected_users: List[str] = Field(default_factory=list)
