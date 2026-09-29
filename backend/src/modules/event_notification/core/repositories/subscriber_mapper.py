from typing import Any, Dict, Tuple

from src.general.repository.redis.redis_base_mapper import BaseRedisMapper

from ...models.subscriber_entity import SubscriberEntity, SubscriberFields


class SubscriberMapper(BaseRedisMapper[SubscriberEntity, SubscriberFields]):
    field_mapping: Dict[SubscriberFields, str] = {
        SubscriberFields.UUID: "uuid",
    }

    key_prefix: str = "subscriber"

    storage_type: str = "hash"

    def get_id_field(self) -> SubscriberFields:
        return SubscriberFields.UUID

    async def to_redis(self, entity: SubscriberEntity) -> Dict[str, Any]:
        return {
            str(SubscriberFields.UUID): entity.uuid,
        }

    async def to_entity(self, data: Dict[str, Any]) -> SubscriberEntity:
        return SubscriberEntity(
            uuid=data.get("uuid"),
        )

    async def to_redis_value(
        self, field: SubscriberFields, value: Any
    ) -> Tuple[str, Any]:
        return str(field), self.serialize_value(value)

    async def to_entity_value(
        self, redis_field: str, value: Any
    ) -> Tuple[SubscriberFields, Any]:
        try:
            field = SubscriberFields(redis_field)
        except ValueError:
            return SubscriberFields.UUID, value
        return field, self.deserialize_value(value)

    async def to_redis_field(self, field: SubscriberFields) -> str:
        return str(field)

    async def to_entity_field(self, redis_field: str) -> SubscriberFields:
        return SubscriberFields(redis_field)
