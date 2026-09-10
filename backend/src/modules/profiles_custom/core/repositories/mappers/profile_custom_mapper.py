from typing import Any, Tuple, Dict, List, Optional
from sqlalchemy.orm import InstrumentedAttribute

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.general.repository.exception import NotConvertableValue
from src.core.logger import get_logger

from ....models.orm.profile_custom_orm import ProfileCustomORM
from ....models.entities.profile_custom_entity import ProfileCustomFields, ProfileCustomEntity

from src.general.processors.base.base_data import base_data_type
from src.general.processors.processor_registry import ProcessorRegistry, get_processor_registry

logger = get_logger(__name__)


class ProfileCustomMapper(BaseMapper[ProfileCustomEntity, ProfileCustomORM, ProfileCustomFields]):
    field_mapping = {
        ProfileCustomFields.UUID: ProfileCustomORM.uuid,
        ProfileCustomFields.NAME: ProfileCustomORM.name,
        ProfileCustomFields.AVATAR_URL: ProfileCustomORM.avatar_url,
        ProfileCustomFields.DATA: ProfileCustomORM.data,
        ProfileCustomFields.UPDATED_AT: ProfileCustomORM.updated_at,
        ProfileCustomFields.USER_UUID: ProfileCustomORM.user_uuid,
    }

    reverse_field_mapping = {
        ProfileCustomORM.uuid: ProfileCustomFields.UUID,
        ProfileCustomORM.name: ProfileCustomFields.NAME,
        ProfileCustomORM.avatar_url: ProfileCustomFields.AVATAR_URL,
        ProfileCustomORM.data: ProfileCustomFields.DATA,
        ProfileCustomORM.updated_at: ProfileCustomFields.UPDATED_AT,
        ProfileCustomORM.user_uuid: ProfileCustomFields.USER_UUID,
    }

    def __init__(self, profile_registry: Optional[ProcessorRegistry] = None):
        self.profile_registry = profile_registry or get_processor_registry()

    async def _prepare_list_to_save(
        self, profile_data: List[base_data_type]
    ) -> List[base_data_type]:
        prepared = []
        for data in profile_data:
            service = self.profile_registry.get_data_service(data.data_type)
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
        self, profile_data: List[base_data_type]
    ) -> List[base_data_type]:
        prepared = []
        for data in profile_data:
            service = self.profile_registry.get_data_service(data.data_type)
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

    def _validate_profile_data(self, value: Any) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise NotConvertableValue(
                value, "profile_data", "Profile data must be a dict"
            )
        return value

    def _normalize_profile_data(self, value: Any) -> Dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            logger.warning(f"Expected dict for DATA, got {type(value)}")
            return {}
        return value

    def _deserialize_data(self, raw: List) -> List[Dict]:
        result = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            data_type = item.get("data_type")
            service = self.profile_registry.get_data_service(data_type) if data_type else None
            model_cls = getattr(service, "data_model", None) if service else None
            if model_cls:
                try:
                    result.append(model_cls(**item))
                    continue
                except Exception as e:
                    logger.error(f"Deserialize error for {data_type}: {e}")
            logger.warning(f"Unknown data_type {data_type}, keeping dict")
            result.append(item)
        return result

    async def prepare_data_to_save(
        self, profile_data: List[base_data_type]
    ) -> List[base_data_type]:
        return await self._prepare_list_to_save(profile_data)

    async def prepare_data_to_use(
        self, profile_data: List[base_data_type]
    ) -> List[base_data_type]:
        return await self._prepare_list_to_use(profile_data)

    async def to_orm(self, entity: ProfileCustomEntity) -> ProfileCustomORM:
        prepared = await self.prepare_data_to_save(entity.data or [])
        return ProfileCustomORM(
            uuid=entity.uuid,
            name=entity.name,
            avatar_url=entity.avatar_url,
            data=[d.model_dump() for d in prepared],  # ← JSON-friendly
            updated_at=entity.updated_at,
            user_uuid=entity.user_uuid,
        )

    async def to_entity(self, orm: ProfileCustomORM) -> ProfileCustomEntity:
        raw = orm.data or []
        # Восстанавливаем BaseData по data_type через registry
        data_models = self._deserialize_data(raw)
        prepared = await self.prepare_data_to_use(data_models)
        return ProfileCustomEntity(
            uuid=orm.uuid,
            name=orm.name,
            avatar_url=orm.avatar_url,
            data=prepared,
            updated_at=orm.updated_at,
            user_uuid=orm.user_uuid,
        )

    async def to_orm_value(
        self, field: ProfileCustomFields, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        orm_field = await self.to_orm_field(field)

        if field == ProfileCustomFields.DATA:
            validated_value = self._validate_profile_data(value)
            return ProfileCustomORM.data, validated_value

        return orm_field, value

    async def to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[ProfileCustomFields, Any]:
        entity_field = await self.to_entity_field(field)

        if entity_field == ProfileCustomFields.DATA:
            normalized_value = self._normalize_profile_data(value)
            return entity_field, normalized_value

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
