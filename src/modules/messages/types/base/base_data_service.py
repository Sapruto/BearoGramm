from abc import ABC, abstractmethod
from typing import Any, Generic

from .base_message_data import base_message_data_type

class BaseDataService(ABC, Generic[base_message_data_type]):
    @abstractmethod
    async def save_data(self, raw_data: Any) -> base_message_data_type:
        pass

    @abstractmethod
    async def delete_data(self, processed_data: base_message_data_type) -> bool:
        pass

    @abstractmethod
    async def prepare_to_save(self, data: base_message_data_type) -> base_message_data_type:
        pass

    @abstractmethod
    async def prepare_to_use(self, data: base_message_data_type) -> base_message_data_type:
        pass
