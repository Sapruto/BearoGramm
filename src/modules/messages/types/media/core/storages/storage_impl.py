from typing import Optional

class StorageImpl:
    def __init__(self):
        pass

    async def upload_file(self, file_content: bytes, filename: str, content_type: Optional[str] = None) -> bool:
        pass

    async def unload_file(self, filename: str) -> bool:
        pass

def get_storage_impl() -> StorageImpl:
    return StorageImpl()
