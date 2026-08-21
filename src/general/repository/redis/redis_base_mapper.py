from abc import ABC, abstractmethod
from typing import Generic, Dict, Any, Tuple, Optional
from src.general.types_var import Entity, Fields

class BaseRedisMapper(Generic[Entity, Fields], ABC):
    field_mapping: Dict[Fields, str] = {}
    reverse_field_mapping: Dict[str, Fields] = {}

    key_prefix: str = ""

    storage_type: str = "hash"

    def __init__(self):
        self._build_reverse_mapping()

    def _build_reverse_mapping(self):
        if not self.reverse_field_mapping and self.field_mapping:
            self.reverse_field_mapping = {
                redis_field: entity_field
                for entity_field, redis_field in self.field_mapping.items()
            }

    @abstractmethod
    def to_redis(self, entity: Entity) -> Dict[str, Any]:
        pass

    @abstractmethod
    def to_entity(self, data: Dict[str, Any]) -> Entity:
        pass

    @abstractmethod
    def to_redis_value(self, field: Fields, value: Any) -> Tuple[str, Any]:
        pass

    @abstractmethod
    def to_entity_value(self, redis_field: str, value: Any) -> Tuple[Fields, Any]:
        pass

    @abstractmethod
    def to_redis_field(self, field: Fields) -> str:
        pass

    @abstractmethod
    def to_entity_field(self, redis_field: str) -> Fields:
        pass

    def get_key(self, entity_id: Any) -> str:
        if not self.key_prefix:
            raise ValueError("key_prefix must be set")
        return f"{self.key_prefix}:{entity_id}"

    def get_id_field(self) -> Optional[Fields]:
        return None

    def get_id_from_entity(self, entity: Entity) -> Optional[Any]:
        id_field = self.get_id_field()
        if id_field and hasattr(entity, id_field):
            return getattr(entity, id_field)
        return None

    def serialize_value(self, value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, (list, dict)):
            import json
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def deserialize_value(self, value: str, target_type: type = str) -> Any:
        if value is None or value == "null":
            return None

        if target_type == bool:
            return value.lower() in ("true", "1", "yes")
        if target_type == int:
            try:
                return int(value)
            except ValueError:
                return None
        if target_type == float:
            try:
                return float(value)
            except ValueError:
                return None
        if target_type in (list, dict):
            import json
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        return value
