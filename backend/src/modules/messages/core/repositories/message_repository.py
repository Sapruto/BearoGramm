from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.database import AsyncSessionLocal
from src.general.repository.sql.sql_base_repository import BaseRepository
from src.general.repository.sql.sql_query import SqlQuery

from .mappers.message_mapper import MessageMapper
from ..db.message_db import MessageManager, get_message_manager
from ...models.entities.message_entity import MessageFields, MessageEntity
from ...models.message_load_options import MessageLoadOptions
from ...models.orm.message_orm import MessageORM


class MessageRepository(BaseRepository[MessageManager, MessageFields, MessageEntity]):
    def __init__(self, manager: Optional[MessageManager] = None):
        mapper = MessageMapper()
        super().__init__(manager=manager or get_message_manager(), mapper=mapper)

    async def _encrypt_text(self, text: Optional[str]) -> Optional[str]:
        if text is None:
            return None
        return await self.mapper.encrypt_text(text)

    async def get_by_uuid(
        self,
        uuid: str,
        load_options: Optional[MessageLoadOptions] = None,
    ) -> Optional[MessageEntity]:
        load_options = load_options or MessageLoadOptions()
        stmt = select(MessageORM).where(MessageORM.uuid == uuid)
        for opt in load_options.loader_options():
            stmt = stmt.options(opt)

        async with AsyncSessionLocal() as session:
            res = await session.execute(stmt)
            orm = res.scalar_one_or_none()
            if orm is None:
                return None
            return await self.mapper.to_entity(orm, load_options)

    async def get_by_chat(
        self,
        chat_uuid: str,
        limit: int = 50,
        before_uuid: Optional[str] = None,
        load_options: Optional[MessageLoadOptions] = None,
    ) -> Sequence[MessageEntity]:
        load_options = load_options or MessageLoadOptions()
        stmt = (
            select(MessageORM)
            .where(MessageORM.chat_uuid == chat_uuid)
            .order_by(MessageORM.created_at.desc())
            .limit(limit)
        )
        if before_uuid:
            subq = (
                select(MessageORM.created_at)
                .where(MessageORM.uuid == before_uuid)
                .scalar_subquery()
            )
            stmt = stmt.where(MessageORM.created_at < subq)

        for opt in load_options.loader_options():
            stmt = stmt.options(opt)

        async with AsyncSessionLocal() as session:
            res = await session.execute(stmt)
            orms = res.scalars().all()
            return await self.mapper.to_entity_many(list(orms), load_options)

    async def get_many_by_uuid(
        self,
        uuids: Sequence[str],
        load_options: Optional[MessageLoadOptions] = None,
    ) -> Sequence[MessageEntity]:
        load_options = load_options or MessageLoadOptions()
        stmt = select(MessageORM).where(MessageORM.uuid.in_(uuids))
        for opt in load_options.loader_options():
            stmt = stmt.options(opt)

        async with AsyncSessionLocal() as session:
            res = await session.execute(stmt)
            orms = res.scalars().all()
            return await self.mapper.to_entity_many(list(orms), load_options)

    async def get_all_with_options(
            self,
            query: SqlQuery[MessageFields],
            load_options: Optional[MessageLoadOptions] = None,
    ) -> Sequence[MessageEntity]:
        load_options = load_options or MessageLoadOptions()

        stmt = select(MessageORM)

        where = await self._build_where(query.filters or {})
        for field, value in where.items():
            stmt = stmt.where(field == value)

        for field, direction in (query.order_by or []):
            orm_field = await self._to_orm_field(field)
            stmt = stmt.order_by(
                orm_field.desc() if direction == "desc" else orm_field.asc()
            )

        if query.limit is not None:
            stmt = stmt.limit(query.limit)
        if query.offset is not None:
            stmt = stmt.offset(query.offset)

        for opt in load_options.loader_options():
            stmt = stmt.options(opt)

        async with AsyncSessionLocal() as session:
            res = await session.execute(stmt)
            orms = res.scalars().all()
            return await self.mapper.to_entity_many(list(orms), load_options)

    async def save_with_relations(self, entity: MessageEntity) -> MessageEntity:
        orm = await self.mapper.to_orm(entity)
        async with AsyncSessionLocal() as session:
            session.add(orm)
            await session.flush()
            await session.commit()
            uuid = orm.uuid

        return await self.get_by_uuid(
            uuid,
            load_options=MessageLoadOptions(extra=True, references=True),
        )

    async def update(self, entity: MessageEntity) -> Optional[MessageEntity]:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(MessageORM)
                .where(MessageORM.uuid == entity.uuid)
                .options(selectinload(MessageORM.extra_data))
            )
            res = await session.execute(stmt)
            orm = res.scalar_one_or_none()
            if orm is None:
                return None

            orm.message_text = await self._encrypt_text(entity.message_text)
            orm.updated_at = entity.updated_at

            if entity.extra_data is not None:
                if orm.extra_data is None:
                    orm.extra_data = await self.mapper.data_mapper.to_orm(
                        entity.extra_data
                    )
                else:
                    orm.extra_data.extra_data_type = entity.extra_data.extra_data_type
                    orm.extra_data.payload = entity.extra_data.payload.model_dump(
                        mode="json"
                    )
                    orm.extra_data.schema_version = entity.extra_data.schema_version
                orm.has_extra_data = True
            else:
                if orm.extra_data is not None:
                    await session.delete(orm.extra_data)
                    orm.extra_data = None
                orm.has_extra_data = False

            await session.flush()
            await session.commit()

        return await self.get_by_uuid(
            entity.uuid,
            load_options=MessageLoadOptions(extra=True, references=True, user=True),
        )

    async def delete_by_uuid(self, uuid: str) -> bool:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(MessageORM)
                .where(MessageORM.uuid == uuid)
                .options(
                    selectinload(MessageORM.extra_data),
                    selectinload(MessageORM.references),
                )
            )
            res = await session.execute(stmt)
            orm = res.scalar_one_or_none()
            if orm is None:
                return False
            await session.delete(orm)
            await session.commit()
            return True


def get_message_repository() -> MessageRepository:
    return MessageRepository()
