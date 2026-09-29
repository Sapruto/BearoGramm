from typing import Optional, Tuple

from .storage_interface import StorageInterface

from src.core.settings import Settings


def get_storage_impl() -> StorageInterface:
    from .storage_local_impl import StorageLocalImpl
    from .storage_s3_impl import StorageS3Impl

    if Settings.ENV == "test" or Settings.ENV == "development":
        return StorageLocalImpl()
    elif Settings.ENV == "sms_ru":
        return StorageS3Impl()
    return StorageLocalImpl()


class StorageAPI:
    def __init__(self, storage_impl: Optional[StorageInterface] = None):
        self.storage_impl = storage_impl or get_storage_impl()

    async def upload_file(
        self, file_content: bytes, filename: str, content_type: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        return await self.storage_impl.upload_file(file_content, filename, content_type)

    async def unload_file(self, filename: str) -> bool:
        return await self.storage_impl.unload_file(filename)

    async def file_exists(self, filename: str) -> bool:
        return await self.storage_impl.file_exists(filename)


def get_storage_api() -> StorageAPI:
    return StorageAPI()
