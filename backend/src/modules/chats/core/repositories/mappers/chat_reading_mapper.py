from typing import Any, Tuple
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.core.logger import get_logger

from ....models.orm.chat_reading_orm import ChatReadingORM
from ....models.entities.chat_reading_entity import ChatReadingFields, ChatReadingEntity


logger = get_logger(__name__)


class ChatReadingMapper(BaseMapper[ChatReadingEntity, ChatReadingORM, ChatReadingFields]):
    field_mapping = {
        ChatReadingFields.UUID: ChatReadingORM.uuid,
        ChatReadingFields.CHAT_UUID: ChatReadingORM.chat_uuid,
        ChatReadingFields.USER_UUID: ChatReadingORM.user_uuid,
        ChatReadingFields.LAST_READ_MESSAGE_UUID: ChatReadingORM.last_read_message_uuid,
        ChatReadingFields.UPDATED_AT: ChatReadingORM.updated_at,
    }

    reverse_field_mapping = {
        ChatReadingORM.uuid: ChatReadingFields.UUID,
        ChatReadingORM.chat_uuid: ChatReadingFields.CHAT_UUID,
        ChatReadingORM.user_uuid: ChatReadingFields.USER_UUID,
        ChatReadingORM.last_read_message_uuid: ChatReadingFields.LAST_READ_MESSAGE_UUID,
        ChatReadingORM.updated_at: ChatReadingFields.UPDATED_AT,
    }

    async def to_orm(self, entity: ChatReadingEntity) -> ChatReadingORM:
        return ChatReadingORM(
            uuid=entity.uuid,
            chat_uuid=entity.chat_uuid,
            user_uuid=entity.user_uuid,
            last_readed_message_uuid=entity.last_read_message_uuid,
            updated_at=entity.updated_at,
        )

    async def to_entity(self, orm: ChatReadingORM) -> ChatReadingEntity:
        return ChatReadingEntity(
            uuid=orm.uuid,
            chat_uuid=orm.chat_uuid,
            user_uuid=orm.user_uuid,
            last_readed_message_uuid=orm.last_read_message_uuid,
            updated_at=orm.updated_at,
        )

    async def to_orm_value(
        self, field: ChatReadingFields, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = await self.to_orm_field(field)

        return orm_field, value

    async def to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[ChatReadingFields, Any]:
        entity_field = await self.to_entity_field(field)

        return entity_field, value

    async def to_orm_field(self, field: ChatReadingFields) -> InstrumentedAttribute:
        orm_field = self.field_mapping.get(field)
        if not orm_field:
            raise ValueError(f"No mapping found for field: {field}")
        return orm_field

    async def to_entity_field(self, field: InstrumentedAttribute) -> ChatReadingFields:
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
