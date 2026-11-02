from typing import Optional, Protocol

from .exceptions import (
    ChecksFailed,
    HasNotChat,
)
from ..models.dto.requests import SendMessageRequest, UpdateMessageRequest
from ..models.dto.responses import (
    SendMessageResponse,
    GetMessagesResponse,
    UpdateMessageResponse,
    DeleteMessageResponse,
)
from ..models.entities.message_entity import MessageEntity

from src.modules.chats.models.entities.chat_entity import ChatEntity
from src.modules.chats.participants import (
    MessageAction,
    ResourceType,
    NotParticipant,
)
from src.core.logger import get_logger
from ...chats.models.entities.chat_reading_entity import ChatReadingEntity

logger = get_logger(__name__)


class PermissionProtocol(Protocol):
    async def validate(
        self,
        user_uuid: str,
        resource_uuid: str,
        resource_type: ResourceType,
        action: Optional[MessageAction] = None,
    ) -> bool:
        pass


class ChatProtocol(Protocol):
    async def get_chat(self, chat_uuid: str) -> ChatEntity:
        pass


class MessageProtocol(Protocol):
    async def send_message(
        self, request: SendMessageRequest, user_uuid: str
    ) -> SendMessageResponse:
        pass

    async def update_message(
        self, request: UpdateMessageRequest, user_uuid: str
    ) -> UpdateMessageResponse:
        pass

    async def delete_message(
        self, message_uuid: str, user_uuid: str
    ) -> DeleteMessageResponse:
        pass

    async def get_message(
        self, message_uuid: str, user_uuid: str
    ) -> MessageEntity:
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

    async def get_around_message(
        self,
        message_uuid: str,
        user_uuid: str,
        span_start: int,
        span_end: int,
    ) -> GetMessagesResponse:
        pass

    async def get_messages_before(
        self, before_uuid: str, limit: int, user_uuid: str
    ) -> GetMessagesResponse:
        pass

    async def get_messages_after(
        self, after_uuid: str, limit: int, user_uuid: str
    ) -> GetMessagesResponse:
        pass

    async def count_messages_after(
        self, chat_uuid: str, after_uuid: Optional[str]
    ) -> int:
        pass


class MarkReadProtocol(Protocol):
    async def mark_read(
        self,
        chat_uuid: str,
        user_uuid: str,
        last_read_message_uuid: Optional[str],
    ) -> ChatReadingEntity:
        pass


class MessageUseCases:
    def __init__(
        self,
        permission_protocol: PermissionProtocol,
        chat_protocol: ChatProtocol,
        message_protocol: MessageProtocol,
        mark_read_protocol: MarkReadProtocol,
    ):
        self._permission_protocol = permission_protocol
        self._chat_protocol = chat_protocol
        self._message_protocol = message_protocol
        self._mark_read_protocol = mark_read_protocol

    async def _check_access(
        self, chat_uuid: str, user_uuid: str, action: MessageAction
    ) -> None:
        has_chat = await self._chat_protocol.get_chat(chat_uuid)
        if not has_chat:
            raise HasNotChat()
        try:
            ok = await self._permission_protocol.validate(
                user_uuid, chat_uuid, ResourceType.CHAT, action
            )
        except NotParticipant:
            raise NotParticipant()
        if not ok:
            raise ChecksFailed()

    async def send_message(
        self, request: SendMessageRequest, user_uuid: str
    ) -> SendMessageResponse:
        await self._check_access(request.chat_uuid, user_uuid, MessageAction.CREATE)
        response = await self._message_protocol.send_message(request, user_uuid)
        await self._mark_read_protocol.mark_read(
            response.message_entity.chat_uuid,
            response.message_entity.user_uuid,
            response.message_entity.uuid
        )
        return response

    async def update_message(
        self, request: UpdateMessageRequest, user_uuid: str
    ) -> UpdateMessageResponse:
        message = await self._message_protocol.get_message(
            request.message_uuid, user_uuid
        )
        await self._check_access(message.chat_uuid, user_uuid, MessageAction.UPDATE)
        return await self._message_protocol.update_message(request, user_uuid)

    async def delete_message(
        self, message_uuid: str, user_uuid: str
    ) -> DeleteMessageResponse:
        message = await self._message_protocol.get_message(message_uuid, user_uuid)
        await self._check_access(message.chat_uuid, user_uuid, MessageAction.DELETE)
        return await self._message_protocol.delete_message(message_uuid, user_uuid)

    async def get_message(
        self, message_uuid: str, user_uuid: str
    ) -> MessageEntity:
        message = await self._message_protocol.get_message(message_uuid, user_uuid)
        await self._check_access(message.chat_uuid, user_uuid, MessageAction.GET)
        return message

    async def get_messages(
            self,
            chat_uuid: str,
            limit: int,
            offset: int,
            user_uuid: str,
            show_new: bool,
    ) -> GetMessagesResponse:
        await self._check_access(chat_uuid, user_uuid, MessageAction.GET)
        return await self._message_protocol.get_messages(
            chat_uuid, limit, offset, user_uuid, show_new
        )

    async def get_around_message(
        self,
        message_uuid: str,
        user_uuid: str,
        span_start: int,
        span_end: int,
    ) -> GetMessagesResponse:
        return await self._message_protocol.get_around_message(
            message_uuid=message_uuid,
            user_uuid=user_uuid,
            span_start=span_start,
            span_end=span_end,
        )

    async def get_messages_before(
        self, before_uuid: str, limit: int, user_uuid: str
    ) -> GetMessagesResponse:
        return await self._message_protocol.get_messages_before(
            before_uuid=before_uuid,
            limit=limit,
            user_uuid=user_uuid,
        )

    async def get_messages_after(
        self, after_uuid: str, limit: int, user_uuid: str
    ) -> GetMessagesResponse:
        return await self._message_protocol.get_messages_after(
            after_uuid=after_uuid,
            limit=limit,
            user_uuid=user_uuid,
        )

    async def count_messages_after(
            self, chat_uuid: str, after_uuid: Optional[str]
    ) -> int:
        return await self._message_protocol.count_messages_after(
            chat_uuid=chat_uuid,
            after_uuid=after_uuid,
        )
