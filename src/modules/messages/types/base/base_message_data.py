from pydantic import BaseModel
from typing import TypeVar

class BaseMessageData(BaseModel):
    data_type: str

base_message_data_type = TypeVar("base_message_data_type", bound=BaseMessageData)
