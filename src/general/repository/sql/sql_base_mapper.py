from abc import ABC, abstractmethod
from typing import Generic, Dict, Any, Tuple
from sqlalchemy.orm import InstrumentedAttribute
from src.general.types_var import ORM, Entity, Fields

class BaseMapper(Generic[Entity, ORM, Fields], ABC):
    field_mapping: Dict[Fields, InstrumentedAttribute] = {}
    reverse_field_mapping: Dict[InstrumentedAttribute, Fields] = {}
    value_mapping: Dict[Fields, Dict[InstrumentedAttribute, Any]] = {}

    def __init__(self):
        self._build_reverse_mapping()

    def _build_reverse_mapping(self):
        if not self.reverse_field_mapping and self.field_mapping:
            self.reverse_field_mapping = {
                orm_field: entity_field
                for entity_field, orm_field in self.field_mapping.items()
            }

    @abstractmethod
    def to_orm(self, entity: Entity) -> ORM:
        pass

    @abstractmethod
    def to_entity(self, orm: ORM) -> Entity:
        pass

    @abstractmethod
    def to_orm_value(self, field: Fields, value: Any) -> Tuple[InstrumentedAttribute, Any]:
        pass

    @abstractmethod
    def to_entity_value(self, field: InstrumentedAttribute, value: Any) -> Tuple[Fields, Any]:
        pass

    @abstractmethod
    def to_orm_field(self, field: Fields) -> InstrumentedAttribute:
        pass

    @abstractmethod
    def to_entity_field(self, field: InstrumentedAttribute) -> Fields:
        pass

    def get_field_name(self, field: InstrumentedAttribute) -> str:
        return str(field).split('.')[-1]
