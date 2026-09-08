from pydantic import Field
from src.modules.messages.types.base.base_message_data import BaseMessageData

TextTypeName = "text_message_type"


class TextData(BaseMessageData):
    data_type: str = Field(default=TextTypeName)
    text: str = Field(default="")
