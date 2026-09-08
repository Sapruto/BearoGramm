from typing import Any, Optional

from .text_data import TextData
from ..base.base_data_processor import BaseDataProcessor

from src.general.security.encyptions.encrypter import get_encrypter, Encrypter


class TextProcessor(BaseDataProcessor[TextData]):
    def __init__(
        self, encrypter: Optional[Encrypter] = None, max_chars: Optional[int] = None
    ):
        self.encrypter = encrypter or get_encrypter()
        self.max_chars = max_chars or 10000

    def _validate(self, text: str) -> bool:
        if not text:
            return False
        if len(text) > self.max_chars:
            return False
        return True

    async def save_data(self, raw_data: Any) -> TextData:
        if isinstance(raw_data, str):
            if not self._validate(str(raw_data)):
                raise ValueError("Not valid str in process")
            return TextData(text=raw_data, data_type="text_message_type")
        raise ValueError(f"Invalid raw data for text: {type(raw_data)}")

    async def delete_data(self, processed_data: TextData) -> bool:
        return True

    async def prepare_to_save(self, data: TextData) -> TextData:
        data.text = await self.encrypter.encrypt(data.text)
        return data

    async def prepare_to_use(self, data: TextData) -> TextData:
        data.text = await self.encrypter.decrypt(data.text)
        return data


def get_text_processor() -> TextProcessor:
    return TextProcessor()
