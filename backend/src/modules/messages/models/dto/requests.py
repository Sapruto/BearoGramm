from pydantic import BaseModel, Field
from typing import Any, List, Tuple


class SendMessageRequest(BaseModel):
    chat_uuid: str = Field(...)

    typing_to_data: List[Tuple[str, Any]] = Field(default=[])


class UpdateMessageRequest(BaseModel):
    message_uuid: str = Field(...)
    typing_to_data: List[Tuple[str, Any]] = Field(default=[])


class DeleteMessageRequest(BaseModel):
    message_uuid: str = Field(...)
