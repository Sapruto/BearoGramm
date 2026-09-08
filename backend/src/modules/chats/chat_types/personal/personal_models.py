from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.modules.profiles_custom import ProfileCustomEntity
from ..chat_types import ChatType


class PersonalChatResponse(BaseModel):
    uuid: str
    chat_type: str = ChatType.PERSONAL
    partner_uuid: str
    created_at: datetime
    updated_at: datetime

    profiles: Optional[Dict[str, ProfileCustomEntity]] = None


class PersonalChatPreview(BaseModel):
    uuid: str
    chat_type: str = ChatType.PERSONAL
    partner_uuid: str
    updated_at: datetime


class PersonalChatCreateRequest(BaseModel):
    other_user_phone: str


class PersonalChatListResponse(BaseModel):
    items: List[PersonalChatPreview]
    total: int
    limit: int
    offset: int


class PartnerResponse(BaseModel):
    chat_uuid: str
    partner_uuid: str


class ParticipantCheckResponse(BaseModel):
    chat_uuid: str
    is_participant: bool


class DeleteChatResponse(BaseModel):
    message: str
    chat_uuid: str
