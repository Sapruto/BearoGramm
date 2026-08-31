from typing import Optional
from datetime import datetime, timedelta
import random
import hashlib

from pydantic import BaseModel
from enum import Enum

from src.general.repository.redis.redis_base_repository import BaseRedisRepository
from src.general.repository.redis.redis_base_mapper import BaseRedisMapper
from src.general.repository.redis.redis_query import RedisQuery
from src.core.redis import get_redis
from src.core.logger import get_logger

logger = get_logger(__name__)

class VerificationCodeEntity(BaseModel):
    user_uuid: str
    phone: str
    code: str
    expired_at: datetime

class VerificationCodeFields(str, Enum):
    USER_UUID = "user_uuid"
    PHONE = "phone"
    CODE = "code"
    EXPIRED_AT = "expired_at"

class VerificationCodeMapper(BaseRedisMapper[VerificationCodeEntity, VerificationCodeFields]):
    key_prefix = "verification_code"
    storage_type = "hash"

    field_mapping = {
        VerificationCodeFields.USER_UUID: "user_uuid",
        VerificationCodeFields.PHONE: "phone",
        VerificationCodeFields.CODE: "code",
        VerificationCodeFields.EXPIRED_AT: "expired_at",
    }

    def to_redis(self, entity: VerificationCodeEntity) -> dict:
        return {
            "user_uuid": entity.user_uuid,
            "phone": entity.phone,
            "code": entity.code,
            "expired_at": entity.expired_at.isoformat(),
        }

    def to_entity(self, data: dict) -> VerificationCodeEntity:
        return VerificationCodeEntity(
            user_uuid=data.get("user_uuid", ""),
            phone=data.get("phone", ""),
            code=data.get("code", ""),
            expired_at=datetime.fromisoformat(data.get("expired_at", datetime.now().isoformat())),
        )

    def to_redis_value(self, field: VerificationCodeFields, value) -> tuple[str, any]:
        redis_field = self.to_redis_field(field)
        if field == VerificationCodeFields.EXPIRED_AT and isinstance(value, datetime):
            return redis_field, value.isoformat()
        return redis_field, str(value) if value is not None else ""

    def to_entity_value(self, redis_field: str, value) -> tuple[VerificationCodeFields, any]:
        entity_field = self.to_entity_field(redis_field)
        if value is None:
            return entity_field, None
        if isinstance(value, bytes):
            value = value.decode()
        if entity_field == VerificationCodeFields.EXPIRED_AT:
            try:
                return entity_field, datetime.fromisoformat(value)
            except:
                return entity_field, None
        return entity_field, value

    def to_redis_field(self, field: VerificationCodeFields) -> str:
        return self.field_mapping.get(field, field.value)

    def to_entity_field(self, redis_field: str) -> VerificationCodeFields:
        for entity_field, redis_str in self.field_mapping.items():
            if redis_str == redis_field:
                return entity_field
        raise ValueError(f"No mapping found: {redis_field}")

    def get_id_field(self) -> Optional[VerificationCodeFields]:
        return VerificationCodeFields.PHONE

    def get_id_from_entity(self, entity: VerificationCodeEntity) -> Optional[any]:
        return entity.phone

class VerificationCodeRepository(BaseRedisRepository[VerificationCodeMapper, VerificationCodeFields, VerificationCodeEntity]):
    def __init__(self, ttl: int = 300):
        super().__init__(get_redis(), VerificationCodeMapper(), ttl)
        self.ttl = ttl

    def _hash(self, phone: str) -> str:
        return hashlib.sha256(phone.encode()).hexdigest()[:16]

    def _get_key(self, entity_id) -> str:
        if isinstance(entity_id, str) and entity_id.startswith('+'):
            entity_id = self._hash(entity_id)
        return super()._get_key(entity_id)

    def gen_code(self) -> str:
        return ''.join(str(random.randint(0, 9)) for _ in range(5))

def get_verification_code_repository() -> VerificationCodeRepository:
    return VerificationCodeRepository()
