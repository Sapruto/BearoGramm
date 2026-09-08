from typing import Optional, List
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

        async with super().manager.__get_session() as session:
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
                .having(len(user_uuids) == func.count(ParticipantORM.user_uuid))
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


def get_personal_repository() -> PersonalRepository:
    return PersonalRepository()
