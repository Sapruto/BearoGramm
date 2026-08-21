from src.general.repository.redis.redis_base_mapper import BaseRedisMapper
from typing import Any, Dict, Tuple, Optional
from datetime import datetime

from ....models.entities.session_entity import SessionEntity, SessionFields

class SessionMapper(BaseRedisMapper[SessionEntity, SessionFields]):
    key_prefix = "session"
    storage_type = "hash"

    field_mapping = {
        SessionFields.USER_UUID: "user_uuid",
        SessionFields.TOKEN: "token",
        SessionFields.EXPIRED_AT: "expired_at",
    }

    def to_redis(self, entity: SessionEntity) -> Dict[str, Any]:
        return {
            "user_uuid": entity.user_uuid,
            "token": entity.token,
            "expired_at": entity.expired_at.isoformat() if entity.expired_at else None,
        }

    def to_entity(self, data: Dict[str, Any]) -> SessionEntity:
        return SessionEntity(
            user_uuid=data.get("user_uuid"),
            token=data.get("token"),
            expires_at=datetime.fromisoformat(data.get("expired_at")) if data.get("expired_at") else None,
        )

    def to_redis_value(self, field: SessionFields, value: Any) -> Tuple[str, Any]:
        redis_field = self.to_redis_field(field)

        if field == SessionFields.EXPIRED_AT:
            if isinstance(value, datetime):
                return redis_field, value.isoformat()
            return redis_field, value
        elif field == SessionFields.USER_UUID:
            return redis_field, str(value) if value else None
        elif field == SessionFields.TOKEN:
            return redis_field, str(value) if value else None

        return redis_field, value

    def to_entity_value(self, redis_field: str, value: Any) -> Tuple[SessionFields, Any]:
        entity_field = self.to_entity_field(redis_field)

        if entity_field == SessionFields.EXPIRED_AT:
            if isinstance(value, str):
                return entity_field, datetime.fromisoformat(value)
            return entity_field, value
        elif entity_field == SessionFields.USER_UUID:
            return entity_field, str(value) if value else None
        elif entity_field == SessionFields.TOKEN:
            return entity_field, str(value) if value else None

        return entity_field, value

    def to_redis_field(self, field: SessionFields) -> str:
        return self.field_mapping.get(field, field.value if hasattr(field, 'value') else str(field))

    def to_entity_field(self, redis_field: str) -> SessionFields:
        return self.reverse_field_mapping.get(redis_field, SessionFields(redis_field))

    def get_id_field(self) -> Optional[SessionFields]:
        return SessionFields.TOKEN

    def get_id_from_entity(self, entity: SessionEntity) -> Optional[Any]:
        return entity.token
