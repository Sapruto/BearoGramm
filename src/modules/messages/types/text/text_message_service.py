from typing import Any, Optional

from .text_message_data import TextMessageData
from ..base.base_data_service import BaseDataService

class TextMessageService(BaseDataService[TextMessageData]):
    def __init__(self, max_chars: Optional[int] = None):
        self.max_chars = max_chars or 10000

    def _validate(self, text: str) -> bool:
        if not text:
            return False
        if len(text) > self.max_chars:
            return False
        return True

    async def process(self, raw_data: Any) -> TextMessageData:
        if isinstance(raw_data, str):
            if not self._validate(str(raw_data)):
                raise ValueError("Not valid str in process")
            return TextMessageData(text=raw_data)

        raise ValueError(f"Invalid raw data for text: {type(raw_data)}")

    async def unprocess(self, processed_data: TextMessageData) -> bool:
        return True

def get_text_message_service() -> TextMessageService:
    return TextMessageService()
