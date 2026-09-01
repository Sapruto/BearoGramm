from typing import Optional

from .websocket_message_service import (
    WebSocketMessageService,
    get_websocket_message_service,
)
from .data_processor import DataProcessor
from ..repositories.message_repository import MessageRepository, get_message_repository
from ...models.dto.requests import (
    SendMessageRequest,
    GetMessagesRequest,
    UpdateMessageRequest,
    DeleteMessageRequest,
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
        if not self.chat_service.chat_exists(chat_uuid):
            return False
        if not self.chat_service.user_in_chat(chat_uuid, user_uuid):
            return False
        if not self.permission_service.validate(user_uuid, chat_uuid, ResourceType.CHAT, action_type):
            return False
        return True

    async def _get_chat_participants(self, chat_uuid: str) -> list[str]:
        return await self.chat_service.get_chat_participants(chat_uuid) or []

    async def send_message(self, request: SendMessageRequest) -> SendMessageResponse:
        process_result = None
        try:
            if not await self._checks_in_chat_service(
                request.chat_uuid, request.user_uuid, MessageAction.CREATE
            ):
                return SendMessageResponse(
                    success=False, error_message="_checks_in_chat_service failed"
                )

            process_result = await self.data_processor.save_data(request.typing_to_data)

            if not process_result.success:
                return SendMessageResponse(
                    success=False,
                    error_message=process_result.error_message
                    or "Failed to process message data",
                )

            entity = MessageEntity(
                chat_uuid=request.chat_uuid,
                message_data=process_result.processed_data,
                user_uuid=request.user_uuid,
            )

            saved_entity = await self.message_repository.save(entity)
            if not saved_entity or not isinstance(saved_entity, MessageEntity):
                return SendMessageResponse(
                    success=False, error_message="Database error"
                )

            notification = {
                "type": "new_message",
                "data": saved_entity.model_dump(mode="json"),
            }
            await self.websocket_service.notify_chat_participants(
                saved_entity.chat_uuid, notification
            )

            return SendMessageResponse(success=True, message_entity=saved_entity)

        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            await self.data_processor.delete_data(
                process_result.processed_data if process_result else []
            )

            return SendMessageResponse(success=False, error_message=str(e))

    async def update_message(
        self, request: UpdateMessageRequest
    ) -> UpdateMessageResponse:
        try:
            query = SqlQuery[MessageFields]()
            query.add_filter(MessageFields.UUID, request.message_uuid)
            message = await self.message_repository.get(query)
            if not message:
                return UpdateMessageResponse(
                    success=False, error_message="Message not found"
                )

            if message.user_uuid != request.user_uuid:
                return UpdateMessageResponse(
                    success=False, error_message="Message not belong to user"
                )

            if not await self._checks_in_chat_service(
                message.chat_uuid, request.user_uuid, MessageAction.UPDATE
            ):
                return UpdateMessageResponse(
                    success=False, error_message="_checks_in_chat_service failed"
                )

            process_result = await self.data_processor.update_data(
                old_message_data=message.message_data,
                new_typing_to_data=request.typing_to_data,
            )
            if not process_result.success:
                return UpdateMessageResponse(
                    success=False,
                    error_message=process_result.error_message
                    or "Failed to process message data",
                )

            message.message_data = process_result.processed_data
            saved_entity = await self.message_repository.update(message)

            if not saved_entity:
                return UpdateMessageResponse(
                    success=False, error_message="Failed to update message"
                )

            notification = {
                "type": "message_updated",
                "data": saved_entity.model_dump(mode="json"),
            }
            await self.websocket_service.notify_chat_participants(
                saved_entity.chat_uuid, notification
            )

            return UpdateMessageResponse(success=True, message_entity=saved_entity)

        except Exception as e:
            logger.error(f"Error in update_message: {e}")
            return UpdateMessageResponse(success=False, error_message=str(e))

    async def delete_message(
        self, request: DeleteMessageRequest
    ) -> DeleteMessageResponse:
        try:
            query = SqlQuery[MessageFields]()
            query.add_filter(MessageFields.UUID, request.message_uuid)
            message = await self.message_repository.get(query)
            if not message:
                return DeleteMessageResponse(
                    success=False, error_message="Message not found"
                )

            if message.user_uuid != request.user_uuid:
                return DeleteMessageResponse(
                    success=False, error_message="Message not belong to user"
                )

            if not await self._checks_in_chat_service(
                message.chat_uuid, request.user_uuid, MessageAction.DELETE
            ):
                return DeleteMessageResponse(
                    success=False, error_message="_checks_in_chat_service failed"
                )

            query = SqlQuery[MessageFields]()
            query.add_filter(MessageFields.UUID, request.message_uuid)
            deleted_count = await self.message_repository.delete(query)

            if deleted_count == 0:
                return DeleteMessageResponse(
                    success=False, error_message="Failed to delete message"
                )

            notification = {
                "type": "message_deleted",
                "data": {"message_uuid": request.message_uuid},
            }
            await self.websocket_service.notify_chat_participants(
                message.chat_uuid, notification
            )
            return DeleteMessageResponse(success=True)

        except Exception as e:
            logger.error(f"Error in delete_message: {e}")
            return DeleteMessageResponse(success=False, error_message=str(e))

    async def get_messages(self, request: GetMessagesRequest) -> GetMessagesResponse:
        try:
            if not await self._checks_in_chat_service(
                request.chat_uuid, request.user_uuid, MessageAction.GET
            ):
                return GetMessagesResponse(
                    success=False,
                    error_message="User not in chat or chat_uuid not correct",
                )

            query = SqlQuery[MessageFields]()
            query.add_filter(MessageFields.CHAT_UUID, request.chat_uuid)

            if request.limit > self.max_limit:
                query.limit = self.max_limit
            else:
                query.limit = request.limit
            query.offset = request.offset

            if request.show_new:
                query.add_order_by(MessageFields.CREATED_AT, "desc")
            else:
                query.add_order_by(MessageFields.CREATED_AT, "asc")

            messages = await self.message_repository.get_all(query)

            return GetMessagesResponse(success=True, message_entity=messages)

        except Exception as e:
            logger.error(f"Error in get_messages: {e}")
            return GetMessagesResponse(success=False, error_message=str(e))


def get_message_service() -> MessageService:
    return MessageService()
