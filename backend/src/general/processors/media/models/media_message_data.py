from pydantic import Field
from ...base.base_data import BaseData

MediaTypeName = "media_type"


class MediaData(BaseData):
    data_type: str = Field(default=MediaTypeName)
    media_url: str = Field(default="")
