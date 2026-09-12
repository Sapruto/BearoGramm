from typing import Dict, Any, Tuple, Optional
from src.general.repository.redis.redis_base_mapper import BaseRedisMapper

from ....models.entities.websocket_state_entity import (
    WebSocketStateFields,
    WebSocketStateEntity,
)


class WebSocketStateMapper(
    BaseRedisMapper[WebSocketStateEntity, WebSocketStateFields]
):
    key_prefix = "ws:user"
    storage_type = "hash"

    field_mapping = {
        WebSocketStateFields.USER_UUID: "user_uuid",
        WebSocketStateFields.ONLINE: "online",
    }

    def get_id_field(self) -> Optional[WebSocketStateFields]:
        return WebSocketStateFields.USER_UUID

    async def to_redis(self, entity: WebSocketStateEntity) -> Dict[str, Any]:
        return {
            "user_uuid": entity.user_uuid,
            "online": self.serialize_value(entity.online),
        }

    async def to_entity(self, data: Dict[str, Any]) -> WebSocketStateEntity:
        return WebSocketStateEntity(
            user_uuid=data.get("user_uuid", ""),
            online=self.deserialize_value(data.get("online"), bool),
        )

    async def to_redis_value(
        self, field: WebSocketStateFields, value: Any
    ) -> Tuple[str, Any]:
        redis_field = await self.to_redis_field(field)

        if field == WebSocketStateFields.ONLINE:
            return redis_field, self.serialize_value(bool(value))

        return redis_field, self.serialize_value(value)

    async def to_entity_value(
        self, redis_field: str, value: Any
    ) -> Tuple[WebSocketStateFields, Any]:
        field = await self.to_entity_field(redis_field)

        if field == WebSocketStateFields.ONLINE:
            return field, self.deserialize_value(value, bool)

        return field, value

    async def to_redis_field(self, field: WebSocketStateFields) -> str:
        return self.field_mapping.get(field, field.value)

    async def to_entity_field(self, redis_field: str) -> WebSocketStateFields:
        return self.reverse_field_mapping.get(
            redis_field, WebSocketStateFields.USER_UUID
        )
