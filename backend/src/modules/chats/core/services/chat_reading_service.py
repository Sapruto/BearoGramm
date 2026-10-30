from typing import List, Optional, Protocol

from src.core.logger import get_logger
from src.general.repository.sql.sql_query import SqlQuery
from src.modules.messages.models.dto.responses import GetMessagesResponse

from ..repositories.chat_reading_repository import (
    ChatReadingRepository,
    get_chat_reading_repository,
)
from ...models.entities.chat_reading_entity import ChatReadingEntity, ChatReadingFields


logger = get_logger(__name__)


class LastReadMessageUuidNotFound(Exception):
    pass


class MessageProtocol(Protocol):
    async def count_messages_after(
        self,
        chat_uuid: str,
        after_uuid: Optional[str],
    ) -> int:
        pass

    async def get_messages(
            self,
            chat_uuid: str,
            limit: int,
            offset: int,
            user_uuid: str,
            show_new: bool,
    ) -> GetMessagesResponse:
        pass


class ChatReadingService:
    def __init__(
        self,
        message_service: MessageProtocol,
        chat_reading_repository: Optional[ChatReadingRepository] = None,
    ):
        self._message_service = message_service
        self._chat_reading_repository = chat_reading_repository or get_chat_reading_repository()

    async def get_reading(
        self, chat_uuid: str, user_uuid: str
    ) -> Optional[ChatReadingEntity]:
        query = (
            SqlQuery[ChatReadingFields]()
            .add_filter(ChatReadingFields.CHAT_UUID, chat_uuid)
            .add_filter(ChatReadingFields.USER_UUID, user_uuid)
        )
        return await self._chat_reading_repository.get(query)

    async def get_unread_count(self, chat_uuid: str, user_uuid: str) -> int:
        reading = await self.get_reading(chat_uuid, user_uuid)
        after_uuid = reading.last_read_message_uuid if reading else None

        return await self._message_service.count_messages_after(
            chat_uuid=chat_uuid,
            after_uuid=after_uuid,
        )

    async def get_unread_counts(
        self, chat_uuids: List[str], user_uuid: str
    ) -> List[int]:
        counts: List[int] = []
        for chat_uuid in chat_uuids:
            counts.append(await self.get_unread_count(chat_uuid, user_uuid))
        return counts

    async def mark_read(
        self,
        chat_uuid: str,
        user_uuid: str,
        last_read_message_uuid: Optional[str],
    ) -> ChatReadingEntity:
        if not last_read_message_uuid:
            response = await self._message_service.get_messages(chat_uuid, 1, 0, user_uuid, True)
            last_read_message_uuid = response.messages[0]
            if not last_read_message_uuid:
                raise LastReadMessageUuidNotFound()

        return await self._chat_reading_repository.save(
            ChatReadingEntity(
                chat_uuid=chat_uuid,
                user_uuid=user_uuid,
                last_read_message_uuid=last_read_message_uuid,
            ),
            to_update=True,
        )


def get_chat_reading_service(
    message_service: MessageProtocol,
) -> ChatReadingService:
    return ChatReadingService(message_service=message_service)
