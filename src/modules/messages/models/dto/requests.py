from pydantic import BaseModel, Field
from typing import Any, List, Tuple

class SendMessageRequest(BaseModel):
    chat_uuid: str = Field(...)
    user_uuid: str = Field(...)

    typing_to_data: List[Tuple[str, Any]] = Field(default=[])

class GetMessagesRequest(BaseModel):
    chat_uuid: str = Field(...)
    user_uuid: str = Field(...)

    limit: int = Field(default=10)
    offset: int = Field(default=0)
    show_new: bool = Field(default=True, description="If this = false, we must show a f*cking old messages else new")
