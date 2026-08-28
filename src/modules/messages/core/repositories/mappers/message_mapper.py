from typing import Any, Tuple, List, Optional
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.general.repository.exception import NotConvertableValue
from src.core.logger import get_logger

from ....models.orm.message_orm import MessageORM
from ....models.entities.message_entity import MessageFields, MessageEntity
from ....types.base.base_message_data import BaseMessageData
from ....types.message_registry import MessageRegistry, get_message_registry

logger = get_logger(__name__)

class MessageMapper(BaseMapper[MessageEntity, MessageORM, MessageFields]):
    field_mapping = {
        MessageFields.UUID: MessageORM.uuid,
        MessageFields.MESSAGE_DATA: MessageORM.message_data,
        MessageFields.CREATED_AT: MessageORM.created_at,
        MessageFields.UPDATED_AT: MessageORM.updated_at,
        MessageFields.CHAT_UUID: MessageORM.chat_uuid,
        MessageFields.USER_UUID: MessageORM.user_uuid
    }

    reverse_field_mapping = {
        MessageORM.uuid: MessageFields.UUID,
        MessageORM.message_data: MessageFields.MESSAGE_DATA,
        MessageORM.created_at: MessageFields.CREATED_AT,
        MessageORM.updated_at: MessageFields.UPDATED_AT,
        MessageORM.chat_uuid: MessageFields.CHAT_UUID,
        MessageORM.user_uuid: MessageFields.USER_UUID
    }

    def __init__(self, message_registry: Optional[MessageRegistry] = None):
        self.message_registry = message_registry or get_message_registry()

    async def _prepare_list_to_save(self, message_data: List[BaseMessageData]) -> List[BaseMessageData]:
        prepared = []
        for data in message_data:
            service = self.message_registry.get_data_service(data.data_type)
            if service:
                try:
                    prepared.append(await service.prepare_to_save(data))
                except Exception as e:
                    logger.error(f"Prepare to save error for {data.data_type}: {e}")
                    prepared.append(data)
            else:
                logger.warning(f"No service for {data.data_type}, keeping original")
                prepared.append(data)
        return prepared

    async def _prepare_list_to_use(self, message_data: List[BaseMessageData]) -> List[BaseMessageData]:
        prepared = []
        for data in message_data:
            service = self.message_registry.get_data_service(data.data_type)
            if service:
                try:
                    prepared.append(await service.prepare_to_use(data))
                except Exception as e:
                    logger.error(f"Prepare to use error for {data.data_type}: {e}")
                    prepared.append(data)
            else:
                logger.warning(f"No service for {data.data_type}, keeping original")
                prepared.append(data)
        return prepared

    def _validate_message_data(self, value: Any) -> List[BaseMessageData]:
        if not isinstance(value, list):
            raise NotConvertableValue(value, "message_data", "Message data must be a list")
        return value

    def _normalize_message_data(self, value: Any) -> List[BaseMessageData]:
        if value is None:
            return []
        if not isinstance(value, list):
            logger.warning(f"Expected list for MESSAGE_DATA, got {type(value)}")
            return []
        return value

    async def prepare_data_to_save(self, message_data: List[BaseMessageData]) -> List[BaseMessageData]:
        return await self._prepare_list_to_save(message_data)

    async def prepare_data_to_use(self, message_data: List[BaseMessageData]) -> List[BaseMessageData]:
        return await self._prepare_list_to_use(message_data)

    def to_orm(self, entity: MessageEntity) -> MessageORM:
        return MessageORM(
            uuid=entity.uuid,
            message_data=entity.message_data,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            chat_uuid=entity.chat_uuid,
            user_uuid=entity.user_uuid
        )

    def to_entity(self, orm: MessageORM) -> MessageEntity:
        return MessageEntity(
            uuid=orm.uuid,
            message_data=orm.message_data,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            chat_uuid=orm.chat_uuid,
            user_uuid=orm.user_uuid
        )

    def to_orm_value(self, field: MessageFields, value: Any) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = self.to_orm_field(field)

        if field == MessageFields.MESSAGE_DATA:
            validated_value = self._validate_message_data(value)
            return MessageORM.message_data, validated_value

        return orm_field, value

    def to_entity_value(self, field: InstrumentedAttribute, value: Any) -> Tuple[MessageFields, Any]:
        entity_field = self.to_entity_field(field)

        if entity_field == MessageFields.MESSAGE_DATA:
            normalized_value = self._normalize_message_data(value)
            return entity_field, normalized_value

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

        raise ValueError(f"No reverse mapping found for field: {field}")

    def get_field_name(self, field: InstrumentedAttribute) -> str:
        return str(field).split('.')[-1]
