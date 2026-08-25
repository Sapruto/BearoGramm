from abc import ABC, abstractmethod
from typing import Any, Generic

from .base_message_data import base_message_data_type

class BaseDataService(ABC, Generic[base_message_data_type]):
    @abstractmethod
    async def process(self, raw_data: Any) -> base_message_data_type:
        pass

    @abstractmethod
    async def unprocess(self, processed_data: base_message_data_type) -> bool:
        pass
