from abc import ABC, abstractmethod
from sqlalchemy import select, delete, update, insert, func, and_
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from enum import Enum
from typing import Generic, Optional, Any, List, Dict

from src.core.database import AsyncSessionLocal
from src.core.logger import get_logger

from ..types_var import ORM

class OnConflictAction(str, Enum):
    UPDATE = "UPDATE"
    NOTHING = "NOTHING"
    
    def __str__(self):
        return self.value
    
class ObjectAlreadyExistsError(Exception): pass
class InvalidTransactionStateError(Exception): pass

logger = get_logger(__name__)

class BaseManager(Generic[ORM], ABC):
    def __init__(self, model: Any, immutable_fields: list = None):
        self.model = model
        self.immutable_fields = list(immutable_fields or []) + [self.identifier_field]

    @property
    @abstractmethod
    def identifier_field(self) -> InstrumentedAttribute:
        pass

    async def get_by_field(self, value: Any, field: InstrumentedAttribute, select_field: Optional[InstrumentedAttribute] = None, session: Optional[AsyncSession] = None, for_update: bool = False) -> Optional[ORM]:
        async with self.__get_session(session) as sess:
            stmt = select(select_field or self.model).where(field == value)
            
            if for_update:
                stmt = stmt.with_for_update()
            
            result = await sess.execute(stmt)
            return result.scalar_one_or_none()
        
    async def get_all(self, where: Optional[Dict[str, Any]] = None, limit: Optional[int] = None, offset: Optional[int] = None, session: Optional[AsyncSession] = None) -> List[ORM]:
        async with self.__get_session(session) as sess:
            stmt = select(self.model)
            if where:
                for field, value in where.items():
                    stmt = stmt.where(field == value)
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)
            result = await sess.execute(stmt)
            return result.scalars().all()
        
    async def count(self, where: Optional[Dict[InstrumentedAttribute, Any]] = None, session: Optional[AsyncSession] = None) -> int:
        async with self.__get_session(session) as sess:
            stmt = select(func.count()).select_from(self.model)
            if where:
                for field, value in where.items():
                    stmt = stmt.where(field == value)
            result = await sess.execute(stmt)
            return result.scalar_one()
        
    async def create(self, model: ORM, on_conflict: OnConflictAction = OnConflictAction.NOTHING, commit: bool = True, session: Optional[AsyncSession] = None) -> Optional[ORM]:
        if not model:
            raise ValueError(f"{self.__class__.__name__}: ORM can't be None")
        
        if not session and not commit:
            raise InvalidTransactionStateError("A commit cannot be false if no session is passed")
        if session and not commit:
            logger.warning("Session provided with commit=False - caller must manage transaction")
        
        async with self.__get_session(session) as sess:
            if on_conflict == OnConflictAction.UPDATE:
                data = {c.name: getattr(model, c.name) for c in self.model.__table__.columns if hasattr(model, c.name)}
                
                stmt = insert(self.model).values(**data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=[self.identifier_field],
                    set_={k: v for k, v in data.items() if k not in [f.name for f in self.immutable_fields]}
                ).returning(self.model)
                
                result = await sess.execute(stmt)
                model = result.scalar_one()
            else:
                existing = await sess.execute(
                    select(self.model).where(
                        self.identifier_field == getattr(model, self.identifier_field.key)
                    )
                )
                existing = existing.scalar_one_or_none()
                
                if existing:
                    raise ObjectAlreadyExistsError("Object was created.")
            
                sess.add(model)

            if commit:
                await sess.commit()
                await sess.refresh(model)

            return model
    
    async def update(self, identifier: Optional[Any] = None, field_identifier: Optional[InstrumentedAttribute] = None, where: Optional[Any] = None, commit: bool = True, session: Optional[AsyncSession] = None, **kwargs) -> Optional[ORM]:
        if where is None and (not identifier or not field_identifier):
            raise ValueError("Either 'where' or ('identifier' and 'field_identifier') must be provided")
        if where is not None and identifier and field_identifier:
            raise ValueError("Cannot use both 'where' and ('identifier' + 'field_identifier') at the same time")

        def get_field_name(field):
            if hasattr(field, 'key'):
                return field.key
            elif hasattr(field, 'name'):
                return field.name
            else:
                return str(field)

        immutable_names = [get_field_name(f) for f in self.immutable_fields]
        for field_name in immutable_names:
            kwargs.pop(field_name, None)
        
        if not kwargs:
            raise ValueError("Update data can't be None")
        
        if not session and not commit:
            raise InvalidTransactionStateError("A commit cannot be false if no session is passed")
        if session and not commit:
            logger.warning("Session provided with commit=False - caller must manage transaction")
        
        async with self.__get_session(session) as sess:
            if isinstance(where, dict):
                conditions = []
                for field, value in where.items():
                    conditions.append(field == value)
                stmt_where = and_(*conditions) if conditions else True
            elif where is not None:
                stmt_where = where
            else:
                stmt_where = field_identifier == identifier

            stmt = (
                update(self.model)
                .where(stmt_where)
                .values(**kwargs)
                .returning(self.model)
            )
            
            result = await sess.execute(stmt)
            model = result.scalar_one_or_none()
            
            if commit:
                await sess.commit()
                if model:
                    await sess.refresh(model)
            
            return model

    async def delete(self, where: Optional[Dict[InstrumentedAttribute, Any]] = None, commit: bool = True, session: Optional[AsyncSession] = None) -> int:
        if not where:
            raise ValueError("Where condition is required for delete")
        async with self.__get_session(session) as sess:
            conditions = [field == value for field, value in where.items()]
            stmt = delete(self.model).where(and_(*conditions))
            result = await sess.execute(stmt)
            if commit:
                await sess.commit()
            return result.rowcount

    async def exists(self, identifier: Any, field_identifier: InstrumentedAttribute, session: Optional[AsyncSession] = None) -> bool:
        async with self.__get_session(session) as sess:
            result = await sess.execute(
                select(field_identifier).where(field_identifier == identifier).limit(1)
            )
            return result.scalar_one_or_none() is not None
        
    @asynccontextmanager
    async def __get_session(self, session: Optional[AsyncSession] = None):
        if session:
            yield session
        else:
            async with AsyncSessionLocal() as new_session:
                yield new_session
