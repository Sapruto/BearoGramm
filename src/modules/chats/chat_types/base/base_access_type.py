from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, TypeVar, Generic

from .base_access_threshold import BaseAccessThreshold

AccessThresholdType = TypeVar("AccessThresholdType", bound=BaseAccessThreshold)

class BaseAccessType(BaseModel, ABC, Generic[AccessThresholdType]):
    user_uuid: str

    @abstractmethod
    def get_threshold(self) -> AccessThresholdType:
        pass

    @abstractmethod
    def get_raw_data(self) -> Any:
        pass

    @abstractmethod
    def get_type(self) -> str:
        pass

definite_access_type = TypeVar("definite_access_type", bound=BaseAccessType)
