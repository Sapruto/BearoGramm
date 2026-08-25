from pydantic import Field
from src.modules.messages.types.base.base_message_data import BaseMessageData

class TextMessageData(BaseMessageData):
    text: str = Field(default="")

TextMessageTypeName = "text_message_type"
