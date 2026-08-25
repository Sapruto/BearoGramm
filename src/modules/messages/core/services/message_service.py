from typing import Any, Optional, List, Tuple
from pydantic import BaseModel, Field

from .websocket_message_service import WebSocketMessageService, get_websocket_message_service
from ..repositories.message_repository import MessageRepository, get_message_repository
from ...models.dto.requests import SendMessageRequest, GetMessagesRequest
from ...models.dto.responses import SendMessageResponse, GetMessagesResponse
from ...models.entities.message_entity import MessageEntity, MessageFields
from ...types.base.base_message_data import BaseMessageData
from ...types.message_registry import MessageRegistry, get_message_registry

from src.modules.chats import ChatServiceAPI, get_chat_service_api
from src.general.repository.sql.sql_query import SqlQuery
from src.core.logger import get_logger

logger = get_logger(__name__)

class ProcessDataResponse(BaseModel):
    success: bool = Field(...)
    processed_data: List[BaseMessageData] = Field(default_factory=list)
    error_message: Optional[str] = Field(default=None)

class MessageService:
    def __init__(self, message_repository: Optional[MessageRepository] = None, message_registry: Optional[MessageRegistry] = None, websocket_service: Optional[WebSocketMessageService] = None, chat_service: Optional[ChatServiceAPI] = None):
        self.message_repository = message_repository or get_message_repository()
        self.message_registry = message_registry or get_message_registry()
        self.websocket_service = websocket_service or get_websocket_message_service()

        self.chat_service = chat_service or get_chat_service_api()

        self.max_limit = 100

    async def _process_data(self, typing_to_data: List[Tuple[str, Any]]) -> ProcessDataResponse:
        processed = []

        for data_type, raw_data in typing_to_data:
            data_service = self.message_registry.get_data_service(data_type)
            if not data_service:
                return ProcessDataResponse(
                    success=False,
                    error_message=f"Unknown data type: {data_type}"
                )

            try:
                result_data = await data_service.process(raw_data)
                processed.append(result_data)

            except Exception as e:
                return ProcessDataResponse(
                    success=False,
                    error_message=f"Error creating {data_type}: {str(e)}"
                )

        return ProcessDataResponse(
            success=True,
            processed_data=processed
        )

    async def _unprocess_data(self, processed_data: List[BaseMessageData]) -> None:
        for data in processed_data:
            data_service = self.message_registry.get_data_service(data.data_type)
            if not data_service:
                continue

            try:
                success = data_service.unprocess(data)
                if not success:
                    logger.error("Error in unprocess data")

            except Exception as e:
                logger.error(f"Error in unprocess_data: {e}")

    async def send_message(self, request: SendMessageRequest) -> SendMessageResponse:
        if not self.chat_service.chat_exists(request.chat_uuid) or not self.chat_service.user_in_chat(request.chat_uuid, request.user_uuid):
            return SendMessageResponse(success=False, error_message="User not in chat or chat_uuid not correct")

        process_result = None
        try:
            process_result = await self._process_data(request.typing_to_data)

            if not process_result.success:
                return SendMessageResponse(
                    success=False,
                    error_message=process_result.error_message or "Failed to process message data"
                )

            entity = MessageEntity(
                chat_uuid=request.chat_uuid,
                message_data=process_result.processed_data
            )

            saved_entity = await self.message_repository.save(entity)
            if not saved_entity or not isinstance(saved_entity, MessageEntity):
                return SendMessageResponse(success=False, error_message="Database error")

            await self.websocket_service.notify_about_message(saved_entity.chat_uuid)

            return SendMessageResponse(
                success=True,
                message_entity=saved_entity
            )

        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            await self._unprocess_data(process_result.processed_data if process_result else [])

            return SendMessageResponse(
                success=False,
                error_message=str(e)
            )

    async def update_message(self, request: UpdateMessageRequest) -> UpdateMessageResponse:
        pass

    async def delete_message(self, request: DeleteMessageRequest) -> DeleteMessageResponse:
        pass

    async def get_messages(self, request: GetMessagesRequest) -> GetMessagesResponse:
        if not self.chat_service.chat_exists(request.chat_uuid) or not self.chat_service.user_in_chat(request.chat_uuid, request.user_uuid):
            return GetMessagesResponse(success=False, error_message="User not in chat or chat_uuid not correct")

        try:
            query = SqlQuery[MessageFields]()
            query.add_filter(MessageFields.CHAT_UUID, request.chat_uuid)

            if request.limit > self.max_limit:
                query.limit = self.max_limit
            else:
                query.limit = request.limit
            query.offset = request.offset

            if request.show_new:
                query.add_order_by(MessageFields.CREATED_AT, 'desc')
            else:
                query.add_order_by(MessageFields.CREATED_AT, 'asc')

            messages = await self.message_repository.get_all(query)

            return GetMessagesResponse(
                success=True,
                message_entity=messages
            )

        except Exception as e:
            logger.error(f"Error in get_messages: {e}")
            return GetMessagesResponse(
                success=False,
                error_message=str(e)
            )

def get_message_service() -> MessageService:
    return MessageService()
