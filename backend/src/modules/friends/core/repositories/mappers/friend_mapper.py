from typing import Any, Tuple
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.core.logger import get_logger

from ....models.orm.friend_orm import FriendORM
from ....models.entities.friend_entity import FriendFields, FriendEntity

logger = get_logger(__name__)


class FriendMapper(BaseMapper[FriendEntity, FriendORM, FriendFields]):
    field_mapping = {
        FriendFields.UUID: FriendORM.uuid,
        FriendFields.USER_UUID1: FriendORM.user_uuid1,
        FriendFields.USER_STATUS1: FriendORM.user_status1,
        FriendFields.USER_UUID2: FriendORM.user_uuid2,
        FriendFields.USER_STATUS2: FriendORM.user_status2,
        FriendFields.INITIATOR_UUID: FriendORM.initiator_uuid,
        FriendFields.CREATED_AT: FriendORM.created_at,
    }

    reverse_field_mapping = {
        FriendORM.uuid: FriendFields.UUID,
        FriendORM.user_uuid1: FriendFields.USER_UUID1,
        FriendORM.user_status1: FriendFields.USER_STATUS1,
        FriendORM.user_uuid2: FriendFields.USER_UUID2,
        FriendORM.user_status2: FriendFields.USER_STATUS2,
        FriendORM.initiator_uuid: FriendFields.INITIATOR_UUID,
        FriendORM.created_at: FriendFields.CREATED_AT,
    }

    async def to_orm(self, entity: FriendEntity) -> FriendORM:
        return FriendORM(
            uuid=entity.uuid,
            user_uuid1=entity.user_uuid1,
            user_status1=entity.user_status1,
            user_uuid2=entity.user_uuid2,
            user_status2=entity.user_status2,
            initiator_uuid=entity.initiator_uuid,
            created_at=entity.created_at,
        )

    async def to_entity(self, orm: FriendORM) -> FriendEntity:
        return FriendEntity(
            uuid=orm.uuid,
            user_uuid1=orm.user_uuid1,
            user_status1=orm.user_status1,
            user_uuid2=orm.user_uuid2,
            user_status2=orm.user_status2,
            initiator_uuid=orm.initiator_uuid,
            created_at=orm.created_at,
        )

    async def to_orm_value(self, field: FriendFields, value: Any) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = await self.to_orm_field(field)
        return orm_field, value

    async def to_entity_value(self, field: InstrumentedAttribute, value: Any) -> Tuple[FriendFields, Any]:
        entity_field = await self.to_entity_field(field)
        return entity_field, value

    async def to_orm_field(self, field: FriendFields) -> InstrumentedAttribute:
        orm_field = self.field_mapping.get(field)
        if not orm_field:
            raise ValueError(f"No mapping found for field: {field}")
        return orm_field

    async def to_entity_field(self, field: InstrumentedAttribute) -> FriendFields:
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
