from abc import ABC, abstractmethod
from typing import Optional, Tuple

class StorageInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def upload_file(self,
        file_content: bytes,
        filename: str,
        content_type: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        pass

    @abstractmethod
    async def unload_file(self, filename: str) -> bool:
        pass

    @abstractmethod
    async def file_exists(self, filename: str) -> bool:
        pass
