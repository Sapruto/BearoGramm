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

    partner_profile: Optional[ProfileCustomEntity] = None


class PersonalChatPreview(BaseModel):
    uuid: str
    chat_type: str = ChatType.PERSONAL
    partner_uuid: str
    partner_profile: Optional[ProfileCustomEntity] = None
    updated_at: datetime


class CreatePersonalChatRequest(BaseModel):
    other_user_phone: str


class GetPersonalChatsResponse(BaseModel):
    items: List[PersonalChatPreview]
    total: int
    limit: int
    offset: int


class GetChatPartnerResponse(BaseModel):
    partner_uuid: str
    partner_profile: Optional[ProfileCustomEntity] = None


class CheckParticipantResponse(BaseModel):
    chat_uuid: str
    is_participant: bool


class DeletePersonalChatResponse(BaseModel):
    message: str
