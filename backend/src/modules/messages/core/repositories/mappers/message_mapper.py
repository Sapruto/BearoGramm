import asyncio
import concurrent.futures
from typing import Any, Tuple, List, Optional, Dict
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.general.repository.exception import NotConvertableValue
from src.core.logger import get_logger

from src.general.processors.base.base_data import BaseData
from src.general.processors.processor_registry import ProcessorRegistry, get_processor_registry

from ....models.orm.message_orm import MessageORM
from ....models.entities.message_entity import MessageFields, MessageEntity

logger = get_logger(__name__)


class MessageMapper(BaseMapper[MessageEntity, MessageORM, MessageFields]):
    field_mapping = {
        MessageFields.UUID: MessageORM.uuid,
        MessageFields.MESSAGE_DATA: MessageORM.message_data,
        MessageFields.CREATED_AT: MessageORM.created_at,
        MessageFields.UPDATED_AT: MessageORM.updated_at,
        MessageFields.CHAT_UUID: MessageORM.chat_uuid,
        MessageFields.USER_UUID: MessageORM.user_uuid,
    }

    reverse_field_mapping = {
        MessageORM.uuid: MessageFields.UUID,
        MessageORM.message_data: MessageFields.MESSAGE_DATA,
        MessageORM.created_at: MessageFields.CREATED_AT,
        MessageORM.updated_at: MessageFields.UPDATED_AT,
        MessageORM.chat_uuid: MessageFields.CHAT_UUID,
        MessageORM.user_uuid: MessageFields.USER_UUID,
    }

    def __init__(self, message_registry: Optional[ProcessorRegistry] = None):
        self.message_registry = message_registry or get_processor_registry()

    def _resolve_data_object(self, data: Any) -> BaseData:
        if isinstance(data, BaseData):
            return data

        data_type = data.get("data_type") if isinstance(data, dict) else None
        service = self.message_registry.get_data_service(data_type)
        model_cls = getattr(service, "data_model", None) if service else None

        if model_cls:
            return model_cls.model_validate(data)

        logger.warning(f"No model found for data_type={data_type}, using BaseData")
        return BaseData.model_validate(data)

    async def _prepare_list_to_save(
        self, message_data: List[BaseData]
    ) -> List[BaseData]:
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

    async def _prepare_list_to_use(
        self, message_data: List[Dict]
    ) -> List[BaseData]:
        prepared = []
        for raw in message_data:
            data = self._resolve_data_object(raw)
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

    def _validate_message_data(self, value: Any) -> List[BaseData]:
        if not isinstance(value, list):
            raise NotConvertableValue(
                value, "message_data", "Message data must be a list"
            )
        return value

    def _normalize_message_data(self, value: Any) -> List[BaseData]:
        if value is None:
            return []
        if not isinstance(value, list):
            logger.warning(f"Expected list for MESSAGE_DATA, got {type(value)}")
            return []
        return value

    def _run_async(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)

        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)

    async def prepare_data_to_save(
        self, message_data: List[BaseData]
    ) -> List[BaseData]:
        return await self._prepare_list_to_save(message_data)

    async def prepare_data_to_use(
        self, message_data: List[Dict]
    ) -> List[BaseData]:
        return await self._prepare_list_to_use(message_data)

    def to_orm(self, entity: MessageEntity) -> MessageORM:
        prepared = self._run_async(self.prepare_data_to_save(entity.message_data))
        return MessageORM(
            uuid=entity.uuid,
            message_data=[item.model_dump(mode="json") for item in prepared],
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            chat_uuid=entity.chat_uuid,
            user_uuid=entity.user_uuid,
        )

    def to_entity(self, orm: MessageORM) -> MessageEntity:
        prepared = self._run_async(self.prepare_data_to_use(orm.message_data))
        return MessageEntity(
            uuid=orm.uuid,
            message_data=prepared,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            chat_uuid=orm.chat_uuid,
            user_uuid=orm.user_uuid,
        )

    def to_orm_value(
        self, field: MessageFields, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = self.to_orm_field(field)

        if field == MessageFields.MESSAGE_DATA:
            validated_value = self._validate_message_data(value)
            return MessageORM.message_data, validated_value

        return orm_field, value

    def to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[MessageFields, Any]:
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
        return str(field).split(".")[-1]
