from typing import Any, Tuple
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.core.logger import get_logger

from ....models.orm.profile_custom_orm import ProfileCustomORM
from ....models.entities.profile_custom_entity import ProfileCustomFields, ProfileCustomEntity


logger = get_logger(__name__)


class ProfileCustomMapper(BaseMapper[ProfileCustomEntity, ProfileCustomORM, ProfileCustomFields]):
    field_mapping = {
        ProfileCustomFields.UUID: ProfileCustomORM.uuid,
        ProfileCustomFields.NAME: ProfileCustomORM.name,
        ProfileCustomFields.AVATAR_URL: ProfileCustomORM.avatar_url,
        ProfileCustomFields.BANNER_COLOR: ProfileCustomORM.banner_color,
        ProfileCustomFields.GENDER: ProfileCustomORM.gender,
        ProfileCustomFields.BIO: ProfileCustomORM.bio,
        ProfileCustomFields.UPDATED_AT: ProfileCustomORM.updated_at,
        ProfileCustomFields.USER_UUID: ProfileCustomORM.user_uuid,
    }

    reverse_field_mapping = {
        ProfileCustomORM.uuid: ProfileCustomFields.UUID,
        ProfileCustomORM.name: ProfileCustomFields.NAME,
        ProfileCustomORM.avatar_url: ProfileCustomFields.AVATAR_URL,
        ProfileCustomORM.banner_color: ProfileCustomFields.BANNER_COLOR,
        ProfileCustomORM.gender: ProfileCustomFields.GENDER,
        ProfileCustomORM.bio: ProfileCustomFields.BIO,
        ProfileCustomORM.updated_at: ProfileCustomFields.UPDATED_AT,
        ProfileCustomORM.user_uuid: ProfileCustomFields.USER_UUID,
    }

    async def to_orm(self, entity: ProfileCustomEntity) -> ProfileCustomORM:
        return ProfileCustomORM(
            uuid=entity.uuid,
            name=entity.name,
            avatar_url=entity.avatar_url,
            banner_color=entity.banner_color,
            gender=entity.gender,
            bio=entity.bio,
            updated_at=entity.updated_at,
            user_uuid=entity.user_uuid,
        )

    async def to_entity(self, orm: ProfileCustomORM) -> ProfileCustomEntity:
        return ProfileCustomEntity(
            uuid=orm.uuid,
            name=orm.name,
            avatar_url=orm.avatar_url,
            banner_color=orm.banner_color,
            gender=orm.gender,
            bio=orm.bio,
            updated_at=orm.updated_at,
            user_uuid=orm.user_uuid,
        )

    async def to_orm_value(
        self, field: ProfileCustomFields, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = await self.to_orm_field(field)
        return orm_field, value

    async def to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[ProfileCustomFields, Any]:
        entity_field = await self.to_entity_field(field)
        return entity_field, value

    async def to_orm_field(self, field: ProfileCustomFields) -> InstrumentedAttribute:
        orm_field = self.field_mapping.get(field)
        if not orm_field:
            raise ValueError(f"No mapping found for field: {field}")
        return orm_field

    async def to_entity_field(self, field: InstrumentedAttribute) -> ProfileCustomFields:
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
