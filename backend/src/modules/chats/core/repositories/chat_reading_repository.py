from typing import Optional

from src.core.database import AsyncSessionLocal
from src.general.repository.sql.sql_base_repository import BaseRepository

from ...models.entities.chat_reading_entity import ChatReadingEntity, ChatReadingFields

from .mappers.chat_reading_mapper import ChatReadingMapper
from ..db.chat_reading_db import ChatReadingManager, get_chat_reading_manager

from sqlalchemy import insert as sa_insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from ...models.orm.chat_reading_orm import ChatReadingORM


def _get_insert(session, model):
    dialect = session.bind.dialect.name
    if dialect == "postgresql":
        return pg_insert(model)
    if dialect == "sqlite":
        return sqlite_insert(model)
    return sa_insert(model)


class ChatReadingRepository(BaseRepository[ChatReadingManager, ChatReadingFields, ChatReadingEntity]):
    def __init__(self, manager: Optional[ChatReadingManager] = None):
        mapper = ChatReadingMapper()
        super().__init__(manager=manager or get_chat_reading_manager(), mapper=mapper)

    async def upsert_last_read(
        self,
        chat_uuid,
        user_uuid,
        last_read_message_uuid,
    ) -> ChatReadingEntity:
        orm_model = self.manager.model

        async with AsyncSessionLocal() as session:
            stmt = _get_insert(session, orm_model).values(
                chat_uuid=str(chat_uuid),
                user_uuid=str(user_uuid),
                last_read_message_uuid=str(last_read_message_uuid),
            )

            stmt = stmt.on_conflict_do_update(
                index_elements=[
                    orm_model.chat_uuid,
                    orm_model.user_uuid,
                ],
                set_={
                    ChatReadingORM.last_read_message_uuid: stmt.excluded.last_read_message_uuid,
                    ChatReadingORM.updated_at: stmt.excluded.updated_at,
                },
            ).returning(orm_model)

            result = await session.execute(stmt)
            await session.commit()
            orm_obj = result.scalar_one()

        return await self._to_entity(orm_obj)


def get_chat_reading_repository() -> ChatReadingRepository:
    return ChatReadingRepository()
