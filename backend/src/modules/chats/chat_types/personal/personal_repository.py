from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_

from src.modules.chats.chat_types.chat_types import ChatType
from src.modules.chats.core.repositories.chat_repository import ChatRepository
from src.modules.chats.models.orm.chat_orm import ChatORM
from src.modules.chats.models.entities.chat_entity import ChatEntity
from src.modules.participants.models.enums import ResourceType
from src.modules.participants.models.orm.participant_orm import ParticipantORM


class PersonalRepository(ChatRepository):
    async def get_personal_chat_by_participants(
            self,
            user_uuids: List[str]
    ) -> Optional[ChatEntity]:
        if len(user_uuids) != 2:
            return None

        async with self.manager._BaseManager__get_session() as session:
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
                    ChatORM.chat_type == ChatType.PERSONAL,
                    ParticipantORM.user_uuid.in_(user_uuids)
                )
                .group_by(ChatORM.uuid)
                .having(func.count(ParticipantORM.user_uuid) == len(user_uuids))
            )

            result = await session.execute(stmt)
            chat_orm = result.scalar_one_or_none()

        if not chat_orm:
            return None

        return ChatEntity(
            uuid=chat_orm.uuid,
            chat_type=chat_orm.chat_type,
            created_at=chat_orm.created_at,
            updated_at=chat_orm.updated_at
        )

    async def get_user_personal_chats(
        self,
        user_uuid: str,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[ChatEntity], int]:

        async with self.manager._BaseManager__get_session() as session:
            user_chat_uuids = (
                select(ParticipantORM.resource_uuid)
                .where(
                    ParticipantORM.user_uuid == user_uuid,
                    ParticipantORM.resource_type == ResourceType.CHAT,
                )
                .scalar_subquery()
            )

            base_where = and_(
                ChatORM.chat_type == ChatType.PERSONAL,
                ChatORM.uuid.in_(user_chat_uuids),
            )

            total: int = (
                await session.execute(
                    select(func.count()).select_from(ChatORM).where(base_where)
                )
            ).scalar_one()

            if total == 0:
                return [], 0

            stmt = (
                select(ChatORM)
                .where(base_where)
                .order_by(ChatORM.updated_at.desc().nullslast())
                .limit(limit)
                .offset(offset)
            )
            chats_orm = (await session.execute(stmt)).scalars().all()

        chats: List[ChatEntity] = [self._to_entity(c) for c in chats_orm]
        return chats, total


def get_personal_repository() -> PersonalRepository:
    return PersonalRepository()
