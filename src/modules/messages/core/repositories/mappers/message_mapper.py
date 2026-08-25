from typing import Any, Tuple
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.general.repository.exception import NotConvertableValue
from src.core.logger import get_logger

from ....models.orm.message_orm import MessageORM
from ....models.entities.message_entity import MessageFields, MessageEntity

logger = get_logger(__name__)

class MessageMapper(BaseMapper[MessageEntity, MessageORM, MessageFields]):
    field_mapping = {
        MessageFields.UUID: MessageORM.uuid,
        MessageFields.MESSAGE_DATA: MessageORM.message_data,
        MessageFields.CREATED_AT: MessageORM.created_at,
        MessageFields.UPDATED_AT: MessageORM.updated_at,
        MessageFields.CHAT_UUID: MessageORM.chat_uuid
    }

    reverse_field_mapping = {
        MessageORM.uuid: MessageFields.UUID,
        MessageORM.message_data: MessageFields.MESSAGE_DATA,
        MessageORM.created_at: MessageFields.CREATED_AT,
        MessageORM.updated_at: MessageFields.UPDATED_AT,
        MessageORM.chat_uuid: MessageFields.CHAT_UUID
    }

    def to_orm(self, entity: MessageEntity) -> MessageORM:
        return MessageORM(
            uuid=entity.uuid,
            message_data=entity.message_data,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            chat_uuid=entity.chat_uuid
        )

    def to_entity(self, orm: MessageORM) -> MessageEntity:
        return MessageEntity(
            uuid=orm.uuid,
            message_data=orm.message_data,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            chat_uuid=orm.chat_uuid
        )

    def to_orm_value(self, field: MessageFields, value: Any) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = self.to_orm_field(field)

        if field == MessageFields.MESSAGE_DATA:
            if not isinstance(value, list):
                raise NotConvertableValue(value, "message_data", "Message data must be a list")
            return MessageORM.message_data, value

        return orm_field, value

    def to_entity_value(self, field: InstrumentedAttribute, value: Any) -> Tuple[MessageFields, Any]:
        entity_field = self.to_entity_field(field)

        if entity_field == MessageFields.MESSAGE_DATA:
            if value is None:
                return entity_field, []
            if not isinstance(value, list):
                logger.warning(f"Expected list for MESSAGE_DATA, got {type(value)}")
                return entity_field, []
            return entity_field, value

        return entity_field, value

    def to_orm_field(self, field: MessageFields) -> InstrumentedAttribute:
        orm_field = self.field_mapping.get(field)
        if not orm_field:
            raise ValueError(f"No mapping found for field: {field}")
        return orm_field

    def to_entity_field(self, field: InstrumentedAttribute) -> MessageFields:
        entity_field = self.reverse_field_mapping.get(field)
        if entity_field:
            return entity_field

        field_name = self.get_field_name(field)
        for orm_attr, entity_enum in self.reverse_field_mapping.items():
            if self.get_field_name(orm_attr) == field_name:
                return entity_enum

        raise ValueError(f"No reverse mapping found for field: {field} (name: {field_name})")

    def get_field_name(self, field: InstrumentedAttribute) -> str:
        return str(field).split('.')[-1]
