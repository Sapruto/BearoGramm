from pydantic import Field
from src.modules.messages.types.base.base_message_data import BaseMessageData

TextMessageTypeName = "text_message_type"


class TextMessageData(BaseMessageData):
    data_type: str = Field(default=TextMessageTypeName)
    text: str = Field(default="")
