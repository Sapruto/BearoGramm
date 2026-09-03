from typing import Any, Optional

from .storages.storage_api import StorageAPI, get_storage_api
from .utils.media_utils import MediaUtils
from .validator.media_validator import MediaValidator
from ..models.media_message_data import MediaMessageData, MediaMessageTypeName
from ...base.base_data_service import BaseDataService
from src.core.logger import get_logger

logger = get_logger(__name__)


class MediaMessageService(BaseDataService[MediaMessageData]):
    def __init__(
        self,
        storage: Optional[StorageAPI] = None,
        media_utils: Optional[MediaUtils] = None,
        validator: Optional[MediaValidator] = None,
    ):
        self.storage = storage or get_storage_api()
        self.media_utils = media_utils or MediaUtils()
        self.validator = validator or MediaValidator()
        self.data_type = MediaMessageTypeName

    def _extract_path(self, url: str) -> Optional[str]:
        try:
            if "storage.beget.cloud" in url:
                parts = url.split("/", 3)
                return parts[3] if len(parts) >= 4 else None

            if "/media/" in url:
                return url.split("/media/", 1)[1]

            from urllib.parse import urlparse

            parsed = urlparse(url)
            return parsed.path.lstrip("/") if parsed.path else None

        except Exception as e:
            logger.error(f"Path extraction error: {e}")
            return None

    async def save_data(self, raw_data: Any) -> MediaMessageData:
        try:
            if isinstance(raw_data, dict):
                content = raw_data.get("content")
                filename = raw_data.get("filename", "file.bin")
                chat_uuid = raw_data.get("chat_uuid")
            elif isinstance(raw_data, bytes):
                content = raw_data
                filename = "file.bin"
                chat_uuid = None
            else:
                raise ValueError("raw_data must be bytes or dict")

            if not content:
                raise ValueError("File content is empty")

            is_valid, error = self.validator.validate(content, filename)
            if not is_valid:
                raise ValueError(error)

            file_path = self.media_utils.generate_path(filename, chat_uuid)
            content_type = self.media_utils.get_content_type(filename)

            success, result = await self.storage.upload_file(
                content, file_path, content_type
            )

            if not success:
                raise ValueError(f"Upload failed: {result}")

            return MediaMessageData(data_type=self.data_type, media_url=result)

        except Exception as e:
            logger.error(f"Media process error: {e}")
            raise

    async def delete_data(self, processed_data: MediaMessageData) -> bool:
        try:
            if not processed_data.media_url:
                return False

            file_path = self._extract_path(processed_data.media_url)
            if not file_path:
                return False

            return await self.storage.unload_file(file_path)

        except Exception as e:
            logger.error(f"Media unprocess error: {e}")
            return False

    async def prepare_to_save(self, data: MediaMessageData) -> MediaMessageData:
        return data

    async def prepare_to_use(self, data: MediaMessageData) -> MediaMessageData:
        return data


def get_media_message_service() -> MediaMessageService:
    return MediaMessageService()
