from pydantic import Field
from ...base.base_message_data import BaseMessageData

MediaMessageTypeName = "media_message_type"


class MediaMessageData(BaseMessageData):
    data_type: str = Field(default=MediaMessageTypeName)
    media_url: str = Field(default="")
