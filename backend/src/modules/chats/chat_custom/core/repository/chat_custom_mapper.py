from typing import Any, Tuple
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.core.logger import get_logger

from src.modules.chats.chat_custom.models.orm.chat_custom_orm import ChatCustomORM
from src.modules.chats.chat_custom.models.entities.chat_custom_entity import ChatCustomFields, ChatCustomEntity


logger = get_logger(__name__)


class ChatCustomMapper(BaseMapper[ChatCustomEntity, ChatCustomORM, ChatCustomFields]):
    field_mapping = {
        ChatCustomFields.UUID: ChatCustomORM.uuid,
        ChatCustomFields.NAME: ChatCustomORM.name,
        ChatCustomFields.AVATAR_UUID: ChatCustomORM.avatar_uuid,
        ChatCustomFields.BANNER_COLOR: ChatCustomORM.banner_color,
        ChatCustomFields.UPDATED_AT: ChatCustomORM.updated_at,
    }

    reverse_field_mapping = {
        ChatCustomORM.uuid: ChatCustomFields.UUID,
        ChatCustomORM.name: ChatCustomFields.NAME,
        ChatCustomORM.avatar_uuid: ChatCustomFields.AVATAR_UUID,
        ChatCustomORM.banner_color: ChatCustomFields.BANNER_COLOR,
        ChatCustomORM.updated_at: ChatCustomFields.UPDATED_AT,
    }

    async def to_orm(self, entity: ChatCustomEntity) -> ChatCustomORM:
        return ChatCustomORM(
            uuid=entity.uuid,
            name=entity.name,
            avatar_uuid=entity.avatar_uuid,
            banner_color=entity.banner_color,
            updated_at=entity.updated_at,
        )

    async def to_entity(self, orm: ChatCustomORM) -> ChatCustomEntity:
        return ChatCustomEntity(
            uuid=orm.uuid,
            name=orm.name,
            avatar_uuid=orm.avatar_uuid,
            updated_at=orm.updated_at,
        )

    async def to_orm_value(
        self, field: ChatCustomFields, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = await self.to_orm_field(field)
        return orm_field, value

    async def to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[ChatCustomFields, Any]:
        entity_field = await self.to_entity_field(field)
        return entity_field, value

    async def to_orm_field(self, field: ChatCustomFields) -> InstrumentedAttribute:
        orm_field = self.field_mapping.get(field)
        if not orm_field:
            raise ValueError(f"No mapping found for field: {field}")
        return orm_field

    async def to_entity_field(self, field: InstrumentedAttribute) -> ChatCustomFields:
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
