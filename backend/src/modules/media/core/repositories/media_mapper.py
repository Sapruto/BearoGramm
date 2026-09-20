from typing import Any, Tuple

from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.general.repository.exception import NotConvertableValue
from src.core.logger import get_logger

from ...models.media_orm import MediaORM
from ...models.media_entity import MediaFields, MediaEntity

logger = get_logger(__name__)


class MediaMapper(BaseMapper[MediaEntity, MediaORM, MediaFields]):
    field_mapping = {
        MediaFields.UUID: MediaORM.uuid,
        MediaFields.URL: MediaORM.url,
        MediaFields.HASH: MediaORM.hash,
        MediaFields.FILENAME: MediaORM.filename,
        MediaFields.CONTENT_TYPE: MediaORM.content_type,
        MediaFields.SIZE: MediaORM.size,
        MediaFields.VERSION: MediaORM.version,
        MediaFields.CREATED_AT: MediaORM.created_at,
    }

    reverse_field_mapping = {
        MediaORM.uuid: MediaFields.UUID,
        MediaORM.url: MediaFields.URL,
        MediaORM.hash: MediaFields.HASH,
        MediaORM.filename: MediaFields.FILENAME,
        MediaORM.content_type: MediaFields.CONTENT_TYPE,
        MediaORM.size: MediaFields.SIZE,
        MediaORM.version: MediaFields.VERSION,
        MediaORM.created_at: MediaFields.CREATED_AT,
    }

    async def to_orm(self, entity: MediaEntity) -> MediaORM:
        return MediaORM(
            uuid=entity.uuid,
            url=entity.url,
            hash=entity.hash,
            filename=entity.filename,
            content_type=entity.content_type,
            size=entity.size,
            version=entity.version,
            created_at=entity.created_at,
        )

    async def to_entity(self, orm: MediaORM) -> MediaEntity:
        return MediaEntity(
            uuid=orm.uuid,
            url=orm.url,
            hash=orm.hash,
            filename=orm.filename,
            content_type=orm.content_type,
            size=orm.size,
            version=orm.version,
            created_at=orm.created_at,
        )

    async def to_orm_value(
        self, field: MediaFields, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = await self.to_orm_field(field)

        if field == MediaFields.URL:
            if not isinstance(value, str):
                raise NotConvertableValue(value, "url", "URL must be a string")
            return orm_field, value

        if field == MediaFields.HASH:
            if not isinstance(value, str):
                raise NotConvertableValue(value, "hash", "Hash must be a string")
            return orm_field, value

        if field == MediaFields.FILENAME:
            if not isinstance(value, str):
                raise NotConvertableValue(
                    value, "filename", "Filename must be a string"
                )
            return orm_field, value

        if field == MediaFields.CONTENT_TYPE:
            if not isinstance(value, str):
                raise NotConvertableValue(
                    value, "content_type", "Content type must be a string"
                )
            return orm_field, value

        if field == MediaFields.SIZE:
            if not isinstance(value, int):
                raise NotConvertableValue(value, "size", "Size must be an integer")
            if value < 0:
                raise NotConvertableValue(
                    value, "size", "Size must be non-negative"
                )
            return orm_field, value

        if field == MediaFields.VERSION:
            if not isinstance(value, int):
                raise NotConvertableValue(
                    value, "version", "Version must be an integer"
                )
            if value < 1:
                raise NotConvertableValue(
                    value, "version", "Version must be >= 1"
                )
            return orm_field, value

        return orm_field, value

    async def to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[MediaFields, Any]:
        entity_field = await self.to_entity_field(field)
        return entity_field, value

    async def to_orm_field(self, field: MediaFields) -> InstrumentedAttribute:
        orm_field = self.field_mapping.get(field)
        if not orm_field:
            raise ValueError(f"No mapping found for field: {field}")
        return orm_field

    async def to_entity_field(self, field: InstrumentedAttribute) -> MediaFields:
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
