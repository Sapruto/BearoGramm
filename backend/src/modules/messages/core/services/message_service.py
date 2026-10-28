from datetime import datetime, timezone
from typing import Optional, Protocol

from src.general.repository.sql.sql_query import SqlQuery
from src.modules.chats.participants import NotParticipant

from .notify_message_event import NotificatorMessageEvents, get_notificator_message_event, MessageEventType
from ..exceptions import (
    ChecksFailed,
    DatabaseSaveFailed,
    MessageNotFoundError,
    MessageNotOwnedByUserError,
    DatabaseUpdateFailed,
    DatabaseDeleteFailed,
    HasNotChat,
)
from ..repositories.message_repository import (
    MessageRepository,
    get_message_repository,
)
from ...models.dto.requests import SendMessageRequest, UpdateMessageRequest
from ...models.dto.responses import (
    SendMessageResponse,
    GetMessagesResponse,
    UpdateMessageResponse,
    DeleteMessageResponse,
)
from ...models.entities.message_entity import MessageEntity, MessageFields
from ...models.message_load_options import MessageLoadOptions

from src.modules.chats.participants import (
    MessageAction,
    ResourceType,
)
from src.core.logger import get_logger


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
    async def get_chat(self, chat_uuid: str):
        pass


class MessageService:
    def __init__(
        self,
        permission_protocol: PermissionProtocol,
        chat_protocol: ChatProtocol,
        message_repository: Optional[MessageRepository] = None,
        notify_service: Optional[NotificatorMessageEvents] = None,
    ):
        self._permission_protocol = permission_protocol
        self._chat_protocol = chat_protocol
        self._message_repository = message_repository or get_message_repository()
        self._notify_service = notify_service or get_notificator_message_event()
        self._max_limit = 100

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

        entity = MessageEntity(
            chat_uuid=request.chat_uuid,
            message_text=request.message_text,
            extra_data=request.extra_data,
            references=request.references,
            is_stated=request.is_stated or False,
            user_uuid=user_uuid,
            created_at=datetime.now(timezone.utc),
        )

        saved_entity = await self._message_repository.save_with_relations(entity)
        if not saved_entity:
            raise DatabaseSaveFailed()

        await self._notify_service.notify_about_message_event(
            message=saved_entity,
            event_type=MessageEventType.CREATE,
        )
        return SendMessageResponse(message_entity=saved_entity)

    async def update_message(
        self, request: UpdateMessageRequest, user_uuid: str
    ) -> UpdateMessageResponse:
        message = await self._message_repository.get_by_uuid(
            request.message_uuid,
            load_options=MessageLoadOptions(extra=True),
        )
        if not message:
            raise MessageNotFoundError()

        if message.user_uuid != user_uuid:
            raise MessageNotOwnedByUserError()

        await self._check_access(message.chat_uuid, user_uuid, MessageAction.UPDATE)

        if request.message_text is not None:
            message.message_text = request.message_text

        if request.extra_data is not None:
            message.extra_data = request.extra_data
        elif request.clear_extra_data:
            message.extra_data = None

        message.updated_at = datetime.now(timezone.utc)

        saved_entity = await self._message_repository.update(message)
        if not saved_entity:
            raise DatabaseUpdateFailed()

        await self._notify_service.notify_about_message_event(
            message=saved_entity,
            event_type=MessageEventType.UPDATE,
        )
        return UpdateMessageResponse(message_entity=saved_entity)

    async def delete_message(
        self, message_uuid: str, user_uuid: str
    ) -> DeleteMessageResponse:
        message = await self._message_repository.get_by_uuid(message_uuid)
        if not message:
            raise MessageNotFoundError()

        if message.user_uuid != user_uuid:
            raise MessageNotOwnedByUserError()

        await self._check_access(message.chat_uuid, user_uuid, MessageAction.DELETE)

        deleted = await self._message_repository.delete_by_uuid(message_uuid)
        if not deleted:
            raise DatabaseDeleteFailed()

        await self._notify_service.notify_about_message_event(
            message=message,
            event_type=MessageEventType.DELETE,
        )
        return DeleteMessageResponse()

    async def get_message(
        self, message_uuid: str, user_uuid: str
    ) -> MessageEntity:
        message = await self._message_repository.get_by_uuid(
            message_uuid,
            load_options=MessageLoadOptions(extra=True, references=True, user=True),
        )
        if not message:
            raise MessageNotFoundError()

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

        query = SqlQuery[MessageFields]()
        query.add_filter(MessageFields.CHAT_UUID, chat_uuid)

        query.limit = min(limit, self._max_limit)
        query.offset = offset

        if show_new:
            query.add_order_by(MessageFields.CREATED_AT, "desc")
        else:
            query.add_order_by(MessageFields.CREATED_AT, "asc")

        messages = await self._message_repository.get_all_with_options(
            query,
            load_options=MessageLoadOptions(extra=True, references=True, user=True),
        )
        return GetMessagesResponse(messages=list(messages))

    async def get_around_message(
        self,
        message_uuid: str,
        user_uuid: str,
        span_start: int,
        span_end: int,
    ) -> GetMessagesResponse:
        if span_start > 0:
            raise ValueError("span_start must be <= 0")
        if span_end < 0:
            raise ValueError("span_end must be >= 0")

        target = await self.get_message(message_uuid, user_uuid)

        left = min(-span_start, self._max_limit)
        right = min(span_end, self._max_limit - left)

        messages = await self._message_repository.get_around(
            chat_uuid=target.chat_uuid,
            message_uuid=target.uuid,
            created_at=target.created_at,
            span_start=left,
            span_end=right,
            load_options=MessageLoadOptions(extra=True, references=True, user=True),
        )
        return GetMessagesResponse(messages=list(messages))

    async def get_messages_before(self, before_uuid: str, limit: int, user_uuid: str) -> GetMessagesResponse:
        return await self.get_around_message(
            message_uuid=before_uuid,
            user_uuid=user_uuid,
            span_start=-min(limit, self._max_limit),
            span_end=0,
        )

    async def get_messages_after(self, after_uuid: str, limit: int, user_uuid: str) -> GetMessagesResponse:
        return await self.get_around_message(
            message_uuid=after_uuid,
            user_uuid=user_uuid,
            span_start=0,
            span_end=min(limit, self._max_limit),
        )


def get_message_service(permission_protocol: PermissionProtocol, chat_protocol: ChatProtocol) -> MessageService:
    return MessageService(permission_protocol, chat_protocol)
