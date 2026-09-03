from typing import Generic, Dict, Optional, Any, List, Tuple, Union, TypeVar
from sqlalchemy.orm import InstrumentedAttribute

from ..interfaces.base_repository_interface import BaseRepositoryInterface

from src.general.db.base_manager import OnConflictAction
from src.core.database import Base
from src.core.logger import get_logger

from src.general.repository.sql.sql_base_mapper import BaseMapper
from src.general.repository.exception import NotConvertableError
from src.general.repository.sql.sql_query import SqlQuery
from src.general.types_var import Entity as EntityType, Fields as FieldsType, Manager

logger = get_logger(__name__)

Mapper = TypeVar("Mapper", bound=BaseMapper)


class BaseRepository(
    Generic[Manager, FieldsType, EntityType],
    BaseRepositoryInterface[SqlQuery[FieldsType], FieldsType, EntityType],
):
    def __init__(self, manager: Manager, mapper: Mapper):
        self.manager = manager
        self.orm_model = manager.model

        self._mapper = mapper

    def _to_orm(self, EntityType: EntityType) -> Base:
        return self._mapper.to_orm(EntityType)

    def _to_entity(self, orm: Any) -> EntityType:
        return self._mapper.to_entity(orm)

    def _to_orm_value(
        self, field: FieldsType, value: Any
    ) -> Tuple[InstrumentedAttribute, Any]:
        return self._mapper.to_orm_value(field, value)

    def _to_entity_value(
        self, field: InstrumentedAttribute, value: Any
    ) -> Tuple[FieldsType, Any]:
        return self._mapper.to_entity_value(field, value)

    def _to_orm_field(self, field: FieldsType) -> InstrumentedAttribute:
        return self._mapper.to_orm_field(field)

    def _to_entity_field(self, field: InstrumentedAttribute) -> FieldsType:
        return self._mapper.to_entity_field(field)

    def _build_where(
        self, filters: Dict[FieldsType, Any]
    ) -> Dict[InstrumentedAttribute, Any]:
        result = {}
        for field, value in (filters or {}).items():
            try:
                orm_field, orm_value = self._to_orm_value(field, value)
                result[orm_field] = orm_value
            except NotConvertableError as e:
                logger.error(f"Skipping filter {field}={value}: {e}")
                raise
        return result

    async def save(self, EntityType: EntityType) -> EntityType:
        try:
            orm_obj = self._to_orm(EntityType)
            result = await self.manager.create(
                orm_obj, on_conflict=OnConflictAction.NOTHING
            )
            return self._to_entity(result)
        except NotConvertableError as e:
            logger.error(f"Conversion error in save: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in save: {e}")
            raise

    async def delete(self, query: SqlQuery[FieldsType]) -> int:
        try:
            where = self._build_where(query.filters or {})
            return await self.manager.delete(where=where)
        except NotConvertableError as e:
            logger.error(f"Conversion error in delete: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in delete: {e}")
            raise

    async def get_by_field(
            self, value: Any, field: FieldsType, select_field: Optional[FieldsType] = None
    ) -> Optional[Union[EntityType, Any]]:
        try:
            if field is None:
                logger.error("Field cannot be None in get_by_field")
                return None

            orm_field = self._to_orm_field(field)
            _, orm_value = self._to_orm_value(field, value)
            orm_select_field = (
                self._to_orm_field(select_field) if select_field else None
            )

            result = await self.manager.get_by_field(
                orm_value, orm_field, orm_select_field
            )

            if result is None:
                return None

            if select_field is not None:
                _, entity_value = self._to_entity_value(orm_select_field, result)
                return entity_value

            return self._to_entity(result)

        except NotConvertableError as e:
            logger.error(f"Conversion error in get_by_field: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_by_field: {e}", exc_info=True)
            raise

    async def get(self, query: SqlQuery[FieldsType]) -> Optional[EntityType]:
        try:
            where = self._build_where(query.filters or {})
            results = await self.manager.get_all(where=where, limit=1)
            return self._to_entity(results[0]) if results else None
        except NotConvertableError as e:
            logger.error(f"Conversion error in get: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get: {e}")
            raise

    async def get_all(self, query: SqlQuery[FieldsType]) -> List[EntityType]:
        try:
            where = self._build_where(query.filters or {})
            results = await self.manager.get_all(
                where=where, limit=query.limit, offset=query.offset
            )
            return [self._to_entity(r) for r in results]
        except NotConvertableError as e:
            logger.error(f"Conversion error in get_all: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_all: {e}")
            raise

    async def count(self, query: SqlQuery[FieldsType]) -> int:
        try:
            where = self._build_where(query.filters or {})
            return await self.manager.count(where=where)
        except NotConvertableError as e:
            logger.error(f"Conversion error in count: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in count: {e}")
            raise
