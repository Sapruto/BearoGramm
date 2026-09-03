from typing import Optional, Tuple

from .storage_impl import StorageImpl, get_storage_impl


class StorageAPI:
    def __init__(self, storage_impl: Optional[StorageImpl] = None):
        self.storage_impl = storage_impl or get_storage_impl()

    async def upload_file(
        self, file_content: bytes, filename: str, content_type: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        return await self.storage_impl.upload_file(file_content, filename, content_type)

    async def unload_file(self, filename: str) -> bool:
        return await self.storage_impl.unload_file(filename)


def get_storage_api() -> StorageAPI:
    return StorageAPI()
