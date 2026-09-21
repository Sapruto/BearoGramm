from datetime import datetime, timezone
from typing import Optional

from src.general.repository.sql.sql_query import SqlQuery
from src.modules.participants.core.exceptions import NotParticipant
from .websocket_message_service import (
    WebSocketMessageService,
    get_websocket_message_service,
)
from ..exceptions import (
    ChecksFailed,
    DatabaseSaveFailed,
    MessageNotFoundError,
    MessageNotOwnedByUserError,
    DatabaseUpdateFailed,
    DatabaseDeleteFailed,
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

from src.modules.participants import (
    PermissionService,
    get_permission_service,
    MessageAction,
    ResourceType,
)
from src.core.logger import get_logger

logger = get_logger(__name__)


class MessageService:
    def __init__(
        self,
        message_repository: Optional[MessageRepository] = None,
        websocket_service: Optional[WebSocketMessageService] = None,
        permission_service: Optional[PermissionService] = None,
    ):
        self.message_repository = message_repository or get_message_repository()
        self.websocket_service = websocket_service or get_websocket_message_service()
        self.permission_service = permission_service or get_permission_service()
        self.max_limit = 100

    async def _check_access(
        self, chat_uuid: str, user_uuid: str, action: MessageAction
    ) -> None:
        try:
            ok = await self.permission_service.validate(
                user_uuid, chat_uuid, ResourceType.CHAT, action
            )
        except NotParticipant:
            raise NotParticipant()
        if not ok:
            raise ChecksFailed()

    async def _notify(self, chat_uuid: str, notification: dict) -> None:
        try:
            await self.websocket_service.notify_chat_participants(chat_uuid, notification)
        except Exception as e:
            logger.error(
                f"Websocket notify failed for chat {chat_uuid}: {e}", exc_info=True
            )

    async def send_message(
        self, request: SendMessageRequest, user_uuid: str
    ) -> SendMessageResponse:
        await self._check_access(request.chat_uuid, user_uuid, MessageAction.CREATE)

        entity = MessageEntity(
            chat_uuid=request.chat_uuid,
            message_text=request.message_text,
            extra_data=request.extra_data,
            references=request.references,
            user_uuid=user_uuid,
            created_at=datetime.now(timezone.utc),
        )

        saved_entity = await self.message_repository.save_with_relations(entity)
        if not saved_entity:
            raise DatabaseSaveFailed()

        await self._notify(
            saved_entity.chat_uuid,
            {"type": "new_message", "data": saved_entity.model_dump(mode="json")},
        )
        return SendMessageResponse(message_entity=saved_entity)

    async def update_message(
        self, request: UpdateMessageRequest, user_uuid: str
    ) -> UpdateMessageResponse:
        message = await self.message_repository.get_by_uuid(
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

        saved_entity = await self.message_repository.update(message)
        if not saved_entity:
            raise DatabaseUpdateFailed()

        await self._notify(
            saved_entity.chat_uuid,
            {"type": "message_updated", "data": saved_entity.model_dump(mode="json")},
        )
        return UpdateMessageResponse(message_entity=saved_entity)

    async def delete_message(
        self, message_uuid: str, user_uuid: str
    ) -> DeleteMessageResponse:
        message = await self.message_repository.get_by_uuid(message_uuid)
        if not message:
            raise MessageNotFoundError()

        if message.user_uuid != user_uuid:
            raise MessageNotOwnedByUserError()

        await self._check_access(message.chat_uuid, user_uuid, MessageAction.DELETE)

        deleted = await self.message_repository.delete_by_uuid(message_uuid)
        if not deleted:
            raise DatabaseDeleteFailed()

        await self._notify(
            message.chat_uuid,
            {"type": "message_deleted", "data": {"message_uuid": message_uuid}},
        )
        return DeleteMessageResponse()

    async def get_message(
        self, message_uuid: str, user_uuid: str
    ) -> MessageEntity:
        message = await self.message_repository.get_by_uuid(
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

        query.limit = min(limit, self.max_limit)
        query.offset = offset

        if not show_new:
            query.add_order_by(MessageFields.CREATED_AT, "desc")
        else:
            query.add_order_by(MessageFields.CREATED_AT, "asc")

        messages = await self.message_repository.get_all_with_options(
            query,
            load_options=MessageLoadOptions(extra=True, references=True, user=True),
        )
        return GetMessagesResponse(message_entity=list(messages))

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

        left = min(-span_start, self.max_limit)
        right = min(span_end, self.max_limit - left)

        messages = await self.message_repository.get_around(
            chat_uuid=target.chat_uuid,
            message_uuid=target.uuid,
            created_at=target.created_at,
            span_start=left,
            span_end=right,
            load_options=MessageLoadOptions(extra=True, references=True, user=True),
        )
        return GetMessagesResponse(message_entity=list(messages))


def get_message_service() -> MessageService:
    return MessageService()
