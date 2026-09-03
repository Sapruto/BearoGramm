from typing import Any, Tuple
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.general.repository.exception import NotConvertableValue
from src.core.logger import get_logger

from ....models.orm.chat_orm import ChatORM
from ....models.entities.chat_entity import ChatFields, ChatEntity


logger = get_logger(__name__)


class ChatMapper(BaseMapper[ChatEntity, ChatORM, ChatFields]):
    field_mapping = {
        ChatFields.UUID: ChatORM.uuid,
        ChatFields.CHAT_TYPE: ChatORM.chat_type,
        ChatFields.CREATED_AT: ChatORM.created_at,
        ChatFields.UPDATED_AT: ChatORM.updated_at,
    }

    reverse_field_mapping = {
        ChatORM.uuid: ChatFields.UUID,
        ChatORM.chat_type: ChatFields.CHAT_TYPE,
        ChatORM.created_at: ChatFields.CREATED_AT,
        ChatORM.updated_at: ChatFields.UPDATED_AT,
    }

    def to_orm(self, entity: ChatEntity) -> ChatORM:
        return ChatORM(
            uuid=entity.uuid,
            accesses=entity.accesses,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_entity(self, orm: ChatORM) -> ChatEntity:
        return ChatEntity(
            uuid=orm.uuid,
            accesses=orm.accesses,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def to_orm_value(
        self, field: ChatFields, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = self.to_orm_field(field)

        return orm_field, value

    def to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[ChatFields, Any]:
        entity_field = self.to_entity_field(field)

        return entity_field, value

    def to_orm_field(self, field: ChatFields) -> InstrumentedAttribute:
        orm_field = self.field_mapping.get(field)
        if not orm_field:
            raise ValueError(f"No mapping found for field: {field}")
        return orm_field

    def to_entity_field(self, field: InstrumentedAttribute) -> ChatFields:
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
