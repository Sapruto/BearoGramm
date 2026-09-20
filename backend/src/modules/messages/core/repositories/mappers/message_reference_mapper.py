from typing import Any, Tuple

from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.core.logger import get_logger

from ....models.orm.message_reference_orm import MessageReferenceORM
from ....models.entities.message_reference_entity import (
    MessageReferenceEntity,
    MessageReferenceFields,
)

logger = get_logger(__name__)


class MessageReferenceMapper(
    BaseMapper[MessageReferenceEntity, MessageReferenceORM, MessageReferenceFields]
):
    field_mapping = {
        MessageReferenceFields.UUID: MessageReferenceORM.uuid,
        MessageReferenceFields.REFERENCE_TYPE: MessageReferenceORM.reference_type,
        MessageReferenceFields.SOURCE_UUID: MessageReferenceORM.source_uuid,
        MessageReferenceFields.TARGET_UUID: MessageReferenceORM.target_uuid,
        MessageReferenceFields.SPAN_START: MessageReferenceORM.span_start,
        MessageReferenceFields.SPAN_END: MessageReferenceORM.span_end,
        MessageReferenceFields.SPAN_ALL: MessageReferenceORM.span_all,
        MessageReferenceFields.CREATED_AT: MessageReferenceORM.created_at,
    }

    reverse_field_mapping = {
        MessageReferenceORM.uuid: MessageReferenceFields.UUID,
        MessageReferenceORM.reference_type: MessageReferenceFields.REFERENCE_TYPE,
        MessageReferenceORM.source_uuid: MessageReferenceFields.SOURCE_UUID,
        MessageReferenceORM.target_uuid: MessageReferenceFields.TARGET_UUID,
        MessageReferenceORM.span_start: MessageReferenceFields.SPAN_START,
        MessageReferenceORM.span_end: MessageReferenceFields.SPAN_END,
        MessageReferenceORM.span_all: MessageReferenceFields.SPAN_ALL,
        MessageReferenceORM.created_at: MessageReferenceFields.CREATED_AT,
    }

    async def to_orm(self, entity: MessageReferenceEntity) -> MessageReferenceORM:
        return MessageReferenceORM(
            uuid=entity.uuid,
            reference_type=entity.reference_type,
            source_uuid=entity.source_uuid,
            target_uuid=entity.target_uuid,
            span_start=entity.span_start,
            span_end=entity.span_end,
            span_all=entity.span_all,
            created_at=entity.created_at,
        )

    async def to_entity(self, orm: MessageReferenceORM) -> MessageReferenceEntity:
        return MessageReferenceEntity(
            uuid=orm.uuid,
            reference_type=orm.reference_type,
            source_uuid=orm.source_uuid,
            target_uuid=orm.target_uuid,
            span_start=orm.span_start,
            span_end=orm.span_end,
            span_all=orm.span_all,
            created_at=orm.created_at,
        )

    async def to_orm_value(
        self, field: MessageReferenceFields, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = await self.to_orm_field(field)
        return orm_field, value

    async def to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[MessageReferenceFields, Any]:
        entity_field = await self.to_entity_field(field)
        return entity_field, value

    async def to_orm_field(self, field: MessageReferenceFields) -> InstrumentedAttribute:
        orm_field = self.field_mapping.get(field)
        if not orm_field:
            raise ValueError(f"No mapping found for field: {field}")
        return orm_field

    async def to_entity_field(self, field: InstrumentedAttribute) -> MessageReferenceFields:
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
