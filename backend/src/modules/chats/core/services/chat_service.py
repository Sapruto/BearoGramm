from typing import List, Optional

from src.core.logger import get_logger
from src.modules.participants import (
    PermissionService,
    get_permission_service,
)

from ..repositories.chat_repository import (
    ChatRepository,
    get_chat_repository,
)
from ...models.entities.chat_entity import ChatEntity

logger = get_logger(__name__)


class ChatService:
    def __init__(
        self,
        chat_repository: Optional[ChatRepository] = None,
        permission_service: Optional[PermissionService] = None,
    ):
        self.chat_repository = chat_repository or get_chat_repository()
        self.permission_service = permission_service or get_permission_service()

    async def get_chat(self, chat_uuid: str) -> Optional[ChatEntity]:
        return await self.chat_repository.get_by_uuid(chat_uuid)

    async def get_participants(self, chat_uuid: str) -> List:
        try:
            participants = await self.permission_service.get_by_resource(chat_uuid)
        except Exception as e:
            logger.error(
                "Failed to get participants for chat %s: %s",
                chat_uuid, e, exc_info=True,
            )
            return []
        return participants or []

    async def get_participant_uuids(self, chat_uuid: str) -> List[str]:
        participants = await self.get_participants(chat_uuid)

        result: List[str] = []
        for p in participants:
            uuid = (
                getattr(p, "user_uuid", None)
                or getattr(p, "uuid", None)
                or p
            )
            if uuid:
                result.append(str(uuid))
        return result

    async def is_participant(self, chat_uuid: str, user_uuid: str) -> bool:
        uuids = await self.get_participant_uuids(chat_uuid)
        return user_uuid in uuids


def get_chat_service() -> ChatService:
    return ChatService()
