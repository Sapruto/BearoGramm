from typing import Optional

from .websocket_message_service import (
    WebSocketMessageService,
    get_websocket_message_service,
)
from src.general.processors.data_processor import DataProcessor
from ..exceptions import (
    ChecksFailed,
    FailedToProcessData,
    DatabaseSaveFailed,
    MessageNotFoundError,
    MessageNotOwnedByUserError,
    DatabaseUpdateFailed,
    DatabaseDeleteFailed,
)
from ..repositories.message_repository import MessageRepository, get_message_repository
from ...models.dto.requests import (
    SendMessageRequest,
    UpdateMessageRequest,
)
from ...models.dto.responses import (
    SendMessageResponse,
    GetMessagesResponse,
    UpdateMessageResponse,
    DeleteMessageResponse,
)
from ...models.entities.message_entity import MessageEntity, MessageFields

from src.modules.chats import ChatServiceAPI, get_chat_service_api
from src.modules.participants import PermissionService, get_permission_service, MessageAction, ResourceType
from src.general.repository.sql.sql_query import SqlQuery
from src.core.logger import get_logger

logger = get_logger(__name__)


class MessageService:
    def __init__(
        self,
        message_repository: Optional[MessageRepository] = None,
        data_processor: Optional[DataProcessor] = None,
        websocket_service: Optional[WebSocketMessageService] = None,
        permission_service: Optional[PermissionService] = None,
        chat_service: Optional[ChatServiceAPI] = None,
    ):
        self.message_repository = message_repository or get_message_repository()
        self.data_processor = data_processor or DataProcessor()
        self.websocket_service = websocket_service or get_websocket_message_service()

        self.permission_service = permission_service or get_permission_service()
        self.chat_service = chat_service or get_chat_service_api()

        self.max_limit = 100

    async def _checks_in_chat_service(
        self, chat_uuid: str, user_uuid: str, action_type: MessageAction
    ) -> bool:
        return await self.permission_service.validate(
            user_uuid, chat_uuid, ResourceType.CHAT, action_type
        )

    async def send_message(self, request: SendMessageRequest, user_uuid: str) -> SendMessageResponse:
        process_result = None
        try:
            if not await self._checks_in_chat_service(
                request.chat_uuid, user_uuid, MessageAction.CREATE
            ):
                raise ChecksFailed()

            process_result = await self.data_processor.save_data(request.typing_to_data)

            if not process_result.success:
                logger.error(process_result.error)
                raise FailedToProcessData()

            entity = MessageEntity(
                chat_uuid=request.chat_uuid,
                message_data=process_result.processed_data,
                user_uuid=user_uuid,
            )

            saved_entity = await self.message_repository.save(entity)
            if not saved_entity or not isinstance(saved_entity, MessageEntity):
                raise DatabaseSaveFailed()

            notification = {
                "type": "new_message",
                "data": saved_entity.model_dump(mode="json"),
            }
            await self.websocket_service.notify_chat_participants(
                saved_entity.chat_uuid, notification
            )

            return SendMessageResponse(message_entity=saved_entity)

        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            await self.data_processor.delete_data(
                process_result.processed_data if process_result else []
            )
            raise

    async def update_message(
        self, request: UpdateMessageRequest, user_uuid: str
    ) -> UpdateMessageResponse:
        query = SqlQuery[MessageFields]()
        query.add_filter(MessageFields.UUID, request.message_uuid)
        message = await self.message_repository.get(query)
        if not message:
            raise MessageNotFoundError()

        if message.user_uuid != user_uuid:
            raise MessageNotOwnedByUserError()

        if not await self._checks_in_chat_service(
            message.chat_uuid, user_uuid, MessageAction.UPDATE
        ):
            raise ChecksFailed()

        process_result = await self.data_processor.update_data(
            old_data=message.message_data,
            new_typing_to_data=request.typing_to_data,
        )
        if not process_result.success:
            raise FailedToProcessData()

        message.message_data = process_result.processed_data
        saved_entity = await self.message_repository.update(message)

        if not saved_entity:
            raise DatabaseUpdateFailed()

        notification = {
            "type": "message_updated",
            "data": saved_entity.model_dump(mode="json"),
        }
        await self.websocket_service.notify_chat_participants(
            saved_entity.chat_uuid, notification
        )

        return UpdateMessageResponse(message_entity=saved_entity)

    async def delete_message(
        self, message_uuid: str, user_uuid: str
    ) -> DeleteMessageResponse:
        query = SqlQuery[MessageFields]()
        query.add_filter(MessageFields.UUID, message_uuid)
        message = await self.message_repository.get(query)
        if not message:
            raise MessageNotFoundError()

        if message.user_uuid != user_uuid:
            raise MessageNotOwnedByUserError()

        if not await self._checks_in_chat_service(
            message.chat_uuid, user_uuid, MessageAction.DELETE
        ):
            raise ChecksFailed()

        query = SqlQuery[MessageFields]()
        query.add_filter(MessageFields.UUID, message_uuid)
        deleted_count = await self.message_repository.delete(query)

        if deleted_count == 0:
            raise DatabaseDeleteFailed()

        notification = {
            "type": "message_deleted",
            "data": {"message_uuid": message_uuid},
        }
        await self.websocket_service.notify_chat_participants(
            message.chat_uuid, notification
        )
        return DeleteMessageResponse()

    async def get_messages(
            self,
            chat_uuid: str,
            limit: int,
            offset: int,
            user_uuid: str,
    show_new: bool,) -> GetMessagesResponse:
        if not await self._checks_in_chat_service(
            chat_uuid, user_uuid, MessageAction.GET
        ):
            raise ChecksFailed()

        query = SqlQuery[MessageFields]()
        query.add_filter(MessageFields.CHAT_UUID, chat_uuid)

        query.limit = min(limit, self.max_limit)
        query.offset = offset

        if show_new:
            query.add_order_by(MessageFields.CREATED_AT, "desc")
        else:
            query.add_order_by(MessageFields.CREATED_AT, "asc")

        messages = await self.message_repository.get_all(query)

        return GetMessagesResponse(message_entity=messages)


def get_message_service() -> MessageService:
    return MessageService()
