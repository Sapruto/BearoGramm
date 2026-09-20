import json

from typing import Any, Tuple
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.general.security.encyptions.encrypter import get_encrypter
from src.core.logger import get_logger

from ....models.orm.message_data_orm import MessageDataORM
from ....models.entities.message_data_entity import (
    MessageDataEntity,
    MessageDataFields,
)
from ....models.extra_data import ExtraData


logger = get_logger(__name__)


_extra_data_adapter = TypeAdapter(ExtraData)
_ENCRYPTED_PREFIX = "enc::"


class MessageDataMapper(
    BaseMapper[MessageDataEntity, MessageDataORM, MessageDataFields]
):
    field_mapping = {
        MessageDataFields.MESSAGE_UUID: MessageDataORM.message_uuid,
        MessageDataFields.EXTRA_DATA_TYPE: MessageDataORM.extra_data_type,
        MessageDataFields.PAYLOAD: MessageDataORM.payload,
        MessageDataFields.SCHEMA_VERSION: MessageDataORM.schema_version,
    }

    reverse_field_mapping = {
        MessageDataORM.message_uuid: MessageDataFields.MESSAGE_UUID,
        MessageDataORM.extra_data_type: MessageDataFields.EXTRA_DATA_TYPE,
        MessageDataORM.payload: MessageDataFields.PAYLOAD,
        MessageDataORM.schema_version: MessageDataFields.SCHEMA_VERSION,
    }

    def __init__(self):
        super().__init__()
        self.encrypter = get_encrypter()

    async def _encrypt_payload(self, payload: dict, sensitive: list[str]) -> dict:
        result = dict(payload)
        for field in sensitive:
            value = result.get(field)
            if value is None:
                continue
            serialized = json.dumps(value, ensure_ascii=False)
            encrypted = await self.encrypter.encrypt(serialized)
            result[field] = f"{_ENCRYPTED_PREFIX}{encrypted}"
        return result

    async def _decrypt_payload(self, payload: dict) -> dict:
        result = {}
        for key, value in payload.items():
            if isinstance(value, str) and value.startswith(_ENCRYPTED_PREFIX):
                encrypted = value[len(_ENCRYPTED_PREFIX):]
                decrypted = await self.encrypter.decrypt(encrypted)
                result[key] = json.loads(decrypted)
            else:
                result[key] = value
        return result

    async def to_orm(self, entity: MessageDataEntity) -> MessageDataORM:
        payload_dict = entity.payload.model_dump(
            mode="json", exclude_computed_fields=True
        )
        payload_dict = await self._encrypt_payload(
            payload_dict, entity.payload.sensitive_fields()
        )
        return MessageDataORM(
            message_uuid=entity.message_uuid,
            extra_data_type=entity.extra_data_type,
            payload=payload_dict,
            schema_version=entity.schema_version,
        )

    async def to_entity(self, orm: MessageDataORM) -> MessageDataEntity:
        raw = await self._decrypt_payload(dict(orm.payload))
        try:
            payload_obj = _extra_data_adapter.validate_python(raw)
        except ValidationError as e:
            logger.error(
                f"Invalid extra_data payload for message={orm.message_uuid} "
                f"type={orm.extra_data_type}: {e}"
            )
            raise

        return MessageDataEntity(
            message_uuid=orm.message_uuid,
            extra_data_type=orm.extra_data_type,
            payload=payload_obj,
            schema_version=orm.schema_version,
        )

    async def to_orm_value(
        self, field: MessageDataFields, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = await self.to_orm_field(field)

        if field == MessageDataFields.PAYLOAD:
            if hasattr(value, "model_dump") and hasattr(value, "sensitive_fields"):
                payload_dict = value.model_dump(mode="json")
                payload_dict = await self._encrypt_payload(
                    payload_dict, value.sensitive_fields()
                )
                return MessageDataORM.payload, payload_dict
            return MessageDataORM.payload, value

        return orm_field, value

    async def to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[MessageDataFields, Any]:
        entity_field = await self.to_entity_field(field)

        if entity_field == MessageDataFields.PAYLOAD and isinstance(value, dict):
            raw = await self._decrypt_payload(value)
            try:
                return entity_field, _extra_data_adapter.validate_python(raw)
            except ValidationError as e:
                logger.error(f"Invalid payload in to_entity_value: {e}")
                raise

        return entity_field, value

    async def to_orm_field(self, field: MessageDataFields) -> InstrumentedAttribute:
        orm_field = self.field_mapping.get(field)
        if not orm_field:
            raise ValueError(f"No mapping found for field: {field}")
        return orm_field

    async def to_entity_field(self, field: InstrumentedAttribute) -> MessageDataFields:
        entity_field = self.reverse_field_mapping.get(field)
        if entity_field:
            return entity_field
        field_name = self.get_field_name(field)
        for orm_attr, entity_enum in self.reverse_field_mapping.items():
            if self.get_field_name(orm_attr) == field_name:
                return entity_enum
        raise ValueError(f"No reverse mapping found for field: {field}")

    def get_field_name(self, field: InstrumentedAttribute) -> str:
        return str(field).split(".")[-1]
