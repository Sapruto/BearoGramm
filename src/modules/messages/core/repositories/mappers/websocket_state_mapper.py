from typing import Dict, Any, Tuple
from src.general.repository.redis.redis_base_mapper import BaseRedisMapper

from ....models.entities.websocket_state_entity import WebSocketStateFields, WebSocketStateEntity

class WebSocketStateMapper(BaseRedisMapper[WebSocketStateEntity, WebSocketStateFields]):
    key_prefix = "ws:user"
    storage_type = "hash"

    field_mapping = {
        WebSocketStateFields.USER_UUID: "user_uuid",
        WebSocketStateFields.ONLINE: "online",
        WebSocketStateFields.LAST_ACTIVE: "last_activity",
    }

    def __init__(self):
        super().__init__()

    def to_redis(self, entity: WebSocketStateEntity) -> Dict[str, Any]:
        return {
            "user_uuid": entity.user_uuid,
            "online": "true" if entity.online else "false",
            "last_activity": "true" if entity.last_activity else "false",
        }

    def to_entity(self, data: Dict[str, Any]) -> WebSocketStateEntity:
        return WebSocketStateEntity(
            user_uuid=data.get("user_uuid", ""),
            online=data.get("online", "false").lower() == "true",
            last_activity=data.get("last_activity", "false").lower() == "true",
        )

    def to_redis_value(self, field: WebSocketStateFields, value: Any) -> Tuple[str, Any]:
        redis_field = self.to_redis_field(field)

        if isinstance(value, bool):
            return redis_field, "true" if value else "false"
        return redis_field, str(value) if value else ""

    def to_entity_value(self, redis_field: str, value: Any) -> Tuple[WebSocketStateFields, Any]:
        field = self.to_entity_field(redis_field)

        if isinstance(value, str):
            return field, value.lower() == "true"
        return field, bool(value)

    def to_redis_field(self, field: WebSocketStateFields) -> str:
        return self.field_mapping.get(field, field.value)

    def to_entity_field(self, redis_field: str) -> WebSocketStateFields:
        return self.reverse_field_mapping.get(redis_field, WebSocketStateFields.USER_UUID)
