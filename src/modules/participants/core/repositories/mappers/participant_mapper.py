from typing import Any
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper

from ....models.entities.participant_entity import ParticipantEntity, ParticipantFields
from ....models.orm.participant_orm import ParticipantORM


class ParticipantMapper(BaseMapper[ParticipantEntity, ParticipantORM, ParticipantFields]):
    field_mapping = {
        ParticipantFields.UUID: ParticipantORM.uuid,
        ParticipantFields.USER_UUID: ParticipantORM.user_uuid,
        ParticipantFields.RESOURCE_UUID: ParticipantORM.resource_uuid,
        ParticipantFields.RESOURCE_TYPE: ParticipantORM.resource_type,
        ParticipantFields.PERMISSIONS: ParticipantORM.permissions,
    }

    def to_orm(self, entity: ParticipantEntity) -> ParticipantORM:
        return ParticipantORM(
            uuid=entity.uuid,
            user_uuid=entity.user_uuid,
            resource_uuid=entity.resource_uuid,
            resource_type=entity.resource_type,
            permissions=entity.permissions,
        )

    def to_entity(self, orm: ParticipantORM) -> ParticipantEntity:
        return ParticipantEntity(
            uuid=orm.uuid,
            user_uuid=orm.user_uuid,
            resource_uuid=orm.resource_uuid,
            resource_type=orm.resource_type,
            permissions=orm.permissions or {},
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def to_orm_value(self, field: ParticipantFields, value: Any):
        return self.to_orm_field(field), value

    def to_entity_value(self, orm_field: InstrumentedAttribute, value: Any):
        return self.to_entity_field(orm_field), value

    def to_orm_field(self, field: ParticipantFields) -> InstrumentedAttribute:
        return self.field_mapping[field]

    def to_entity_field(self, orm_field: InstrumentedAttribute) -> ParticipantFields:
        return self.reverse_field_mapping[orm_field]
