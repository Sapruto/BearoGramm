from pydantic import Field
from ..base.base_data import BaseData

TextTypeName = "text_message_type"


class TextData(BaseData):
    data_type: str = Field(default=TextTypeName)
    text: str = Field(default="")
