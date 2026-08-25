from pydantic import Field
from ...base.base_message_data import BaseMessageData

class MediaMessageData(BaseMessageData):
    media_url: str = Field(default="")

MediaMessageTypeName = "media_message_type"
