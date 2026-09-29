from typing import Optional, Tuple

from .storage_interface import StorageInterface
from ..utils.media_utils import MediaUtils

from src.core.settings import Settings
from src.core.logger import get_logger


logger = get_logger(__name__)


class StorageLocalImpl(StorageInterface):
    def __init__(self):
        super().__init__()
        self.media_utils = MediaUtils()
        self.upload_dir = Settings.MEDIA_STORAGE.UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self, file_content: bytes, filename: str, content_type: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        try:
            file_path = self.media_utils.generate_path(filename)

            full_path = self.upload_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "wb") as f:
                f.write(file_content)

            url = f"/media/{file_path}"
            logger.info(f"File saved locally: {file_path}")

            return True, url

        except Exception as e:
            logger.error(f"Local upload error: {e}")
            return False, f"Local upload failed: {str(e)}"

    async def unload_file(self, filename: str) -> bool:
        try:
            file_path = self.upload_dir / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Local file deleted: {filename}")
                return True
            else:
                logger.warning(f"Local file not found: {filename}")
                return False

        except Exception as e:
            logger.error(f"Local delete error: {e}")
            return False

    async def file_exists(self, filename: str) -> bool:
        file_path = self.upload_dir / filename
        return file_path.exists()


def get_storage_local_impl() -> StorageLocalImpl:
    return StorageLocalImpl()
