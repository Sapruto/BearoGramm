from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_

from src.core.database import AsyncSessionLocal
from src.modules.chats.chat_types.chat_types import ChatType
from src.modules.chats.models.orm.chat_orm import ChatORM
from src.modules.chats.models.entities.chat_entity import ChatEntity, ChatFields
from src.modules.participants.models.enums import ResourceType
from src.modules.participants.models.orm.participant_orm import ParticipantORM
from src.general.repository.sql.sql_base_repository import BaseRepository

from .mappers.chat_mapper import ChatMapper
from ..db.chat_db import ChatManager, get_chat_manager


class ChatRepository(BaseRepository[ChatManager, ChatFields, ChatEntity]):
    def __init__(self, manager: Optional[ChatManager] = None):
        mapper = ChatMapper()
        super().__init__(manager=manager or get_chat_manager(), mapper=mapper)

    async def get_chat_by_participants(
            self,
            user_uuids: List[str],
            chat_type: ChatType = ChatType.DEFAULT,
    ) -> Optional[ChatEntity]:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(ChatORM)
                .join(
                    ParticipantORM,
                    and_(
                        ParticipantORM.resource_uuid == ChatORM.uuid,
                        ParticipantORM.resource_type == ResourceType.CHAT
                    )
                )
                .where(
                    ChatORM.chat_type == chat_type,
                    ParticipantORM.user_uuid.in_(user_uuids)
                )
                .group_by(ChatORM.uuid)
                .having(func.count(ParticipantORM.user_uuid) == len(user_uuids))
            )

            result = await session.execute(stmt)
            chat_orm = result.scalar_one_or_none()

        if not chat_orm:
            return None

        return await self._to_entity(chat_orm)

    async def get_user_chats(
        self,
        user_uuid: str,
        limit: int = 50,
        offset: int = 0,
        show_new: bool = True,
        chat_type: ChatType = ChatType.DEFAULT
    ) -> Tuple[List[ChatEntity], int]:
        async with AsyncSessionLocal() as session:
            user_chat_uuids = (
                select(ParticipantORM.resource_uuid)
                .where(
                    ParticipantORM.user_uuid == user_uuid,
                    ParticipantORM.resource_type == ResourceType.CHAT,
                )
                .scalar_subquery()
            )

            base_where = and_(
                ChatORM.chat_type == chat_type,
                ChatORM.uuid.in_(user_chat_uuids),
            )

            total: int = (
                await session.execute(
                    select(func.count()).select_from(ChatORM).where(base_where)
                )
            ).scalar_one()

            if total == 0:
                return [], 0

            order_by_clause = (
                ChatORM.updated_at.desc().nullslast()
                if show_new
                else ChatORM.updated_at.asc().nullsfirst()
            )

            stmt = (
                select(ChatORM)
                .where(base_where)
                .order_by(order_by_clause)
                .limit(limit)
                .offset(offset)
            )
            chats_orm = (await session.execute(stmt)).scalars().all()

        chats: List[ChatEntity] = [await self._to_entity(c) for c in chats_orm]
        return chats, total


def get_chat_repository() -> ChatRepository:
    return ChatRepository()
