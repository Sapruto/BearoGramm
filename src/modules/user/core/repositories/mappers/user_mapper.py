from typing import Any, Tuple, Optional
from sqlalchemy.orm import InstrumentedAttribute
import asyncio
import hashlib

from src.general.security.encyptions.encrypter import Encrypter, get_encrypter
from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.general.repository.exception import NotConvertableValue
from src.core.settings import Settings
from src.core.logger import get_logger

from ....models.orm.user_orm import UserORM
from ....models.entities.user_entity import UserFields, UserEntity

logger = get_logger(__name__)


class UserMapper(BaseMapper[UserEntity, UserORM, UserFields]):
    field_mapping = {
        UserFields.UUID: UserORM.uuid,
        UserFields.PHONE_NUMBER: UserORM.phone_number_encrypted,
        UserFields.PHONE_NUMBER_HASH: UserORM.phone_number_hash,
        UserFields.PHONE_NUMBER_MASK: UserORM.phone_number_mask,
        UserFields.CREATED_AT: UserORM.created_at,
        UserFields.UPDATED_AT: UserORM.updated_at,
    }

    reverse_field_mapping = {
        UserORM.uuid: UserFields.UUID,
        UserORM.phone_number_encrypted: UserFields.PHONE_NUMBER,
        UserORM.phone_number_hash: UserFields.PHONE_NUMBER_HASH,
        UserORM.phone_number_mask: UserFields.PHONE_NUMBER_MASK,
        UserORM.created_at: UserFields.CREATED_AT,
        UserORM.updated_at: UserFields.UPDATED_AT,
    }

    def __init__(self, encrypter: Optional[Encrypter] = None):
        self.encrypter = encrypter or get_encrypter()
        self.hash_salt = Settings.PHONE.HASH_SALT

    def _normalize_phone(self, phone: str) -> str:
        cleaned = "".join(filter(str.isdigit, phone))

        if cleaned.startswith("8"):
            cleaned = "7" + cleaned[1:]
        if not cleaned.startswith("7"):
            cleaned = "7" + cleaned

        return f"+{cleaned}"

    def _hash_phone(self, phone: str) -> str:
        normalized = self._normalize_phone(phone)
        return hashlib.sha256(
            f"{self.hash_salt}:{normalized}".encode("utf-8")
        ).hexdigest()

    def _mask_phone(self, phone: str) -> str:
        normalized = self._normalize_phone(phone)
        if len(normalized) >= 11:
            return f"{normalized[:2]}***{normalized[-4:]}"
        return phone

    def to_orm(self, entity: UserEntity) -> UserORM:
        phone_encrypted = None
        phone_hash = None
        phone_mask = None

        if entity.phone_number:
            try:
                loop = asyncio.get_event_loop()
                phone_encrypted = loop.run_until_complete(
                    self.encrypter.encrypt_field(entity.phone_number)
                )
            except RuntimeError:
                phone_encrypted = asyncio.run(
                    self.encrypter.encrypt_field(entity.phone_number)
                )

            phone_hash = self._hash_phone(entity.phone_number)
            phone_mask = self._mask_phone(entity.phone_number)

        return UserORM(
            uuid=entity.uuid,
            phone_number_encrypted=phone_encrypted,
            phone_number_hash=phone_hash,
            phone_number_mask=phone_mask,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_entity(self, orm: UserORM) -> UserEntity:
        phone_number = None

        if orm.phone_number_encrypted:
            try:
                if hasattr(self, "_loop"):
                    phone_number = self._loop.run_until_complete(
                        self.encrypter.decrypt_field(orm.phone_number_encrypted)
                    )
                else:
                    phone_number = asyncio.run(
                        self.encrypter.decrypt_field(orm.phone_number_encrypted)
                    )
            except Exception as e:
                logger.error(f"Failed to decrypt phone: {e}")
                phone_number = None

        return UserEntity(
            uuid=orm.uuid,
            phone_number=phone_number if phone_number is not None else "",
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def to_orm_value(
        self, field: UserFields, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = self.to_orm_field(field)

        if field == UserFields.PHONE_NUMBER:
            if not isinstance(value, str):
                raise NotConvertableValue(
                    value, "phone_number", "Phone number must be a string"
                )

            phone_hash = self._hash_phone(value)
            return UserORM.phone_number_hash, phone_hash

        return orm_field, value

    def to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[UserFields, Any]:
        entity_field = self.to_entity_field(field)

        if entity_field == UserFields.PHONE_NUMBER:
            if value is None:
                return entity_field, None
            try:
                decrypted = asyncio.run(self.encrypter.decrypt_field(value))
                return entity_field, decrypted
            except Exception as e:
                logger.error(f"Failed to decrypt phone in to_entity_value: {e}")
                return entity_field, None

        return entity_field, value

    def to_orm_field(self, field: UserFields) -> InstrumentedAttribute:
        orm_field = self.field_mapping.get(field)
        if not orm_field:
            raise ValueError(f"No mapping found for field: {field}")
        return orm_field

    def to_entity_field(self, field: InstrumentedAttribute) -> UserFields:
        entity_field = self.reverse_field_mapping.get(field)
        if entity_field:
            return entity_field

        field_name = self.get_field_name(field)
        for orm_attr, entity_enum in self.reverse_field_mapping.items():
            if self.get_field_name(orm_attr) == field_name:
                return entity_enum

        raise ValueError(
            f"No reverse mapping found for field: {field} (name: {field_name})"
        )

    def get_field_name(self, field: InstrumentedAttribute) -> str:
        return str(field).split(".")[-1]
