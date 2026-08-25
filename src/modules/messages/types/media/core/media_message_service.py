from typing import Any, Optional

from .storages.storage_api import StorageAPI, get_storage_api
from ..models.media_message_data import MediaMessageData
from ...base.base_data_service import BaseDataService

class MediaMessageService(BaseDataService[MediaMessageData]):
    def __init__(self, media_storage: Optional[StorageAPI] = None):
        self.storage = media_storage or get_storage_api()

    async def process(self, raw_data: Any) -> MediaMessageData:
        pass

    async def unprocess(self, processed_data: MediaMessageData) -> bool:
        pass

def get_media_message_service() -> MediaMessageService:
    return MediaMessageService()
