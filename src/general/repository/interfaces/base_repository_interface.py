from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Optional, List

from .query_interface import QueryInterface
from ...types_var import Entity, Fields

QueryType = TypeVar("QueryType", bound=QueryInterface)


class BaseRepositoryInterface(Generic[QueryType, Fields, Entity], ABC):
    @abstractmethod
    async def save(self, entity: Entity) -> Entity:
        pass

    @abstractmethod
    async def delete(self, query: QueryType) -> int:
        pass

    @abstractmethod
    async def get_by_field(
        self, value: Any, field: Fields, select_field: Optional[Fields] = None
    ) -> Optional[Entity]:
        pass

    @abstractmethod
    async def get(self, query: QueryType) -> Optional[Entity]:
        pass

    @abstractmethod
    async def get_all(self, query: QueryType) -> List[Entity]:
        pass

    @abstractmethod
    async def count(self, query: QueryType) -> int:
        pass
