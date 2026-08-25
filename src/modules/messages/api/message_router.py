from fastapi import APIRouter, WebSocket, Depends

from src.modules.user import get_current_user_depends, UserEntity
from src.core.logger import get_logger

from .message_router_names import MessageRoutes
from ..core.services.message_service import get_message_service, MessageService
from ..models.dto.requests import SendMessageRequest, GetMessagesRequest
from ..models.dto.responses import SendMessageResponse, GetMessagesResponse

logger = get_logger(__name__)

message_router = APIRouter(prefix=MessageRoutes.base)

@message_router.websocket(MessageRoutes.ws_messages)
async def messages_websocket(websocket: WebSocket, chat_uuid: str, user_uuid: str):
    pass

@message_router.post(MessageRoutes.send_message, response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest, service: MessageService = Depends(get_message_service), current_user: UserEntity = Depends(get_current_user_depends())):
    if request.user_uuid != current_user.uuid:
        return SendMessageResponse(success=False, error_message="request.user_uuid != current_user.uuid")

    result = await service.send_message(request)
    return result

@message_router.get(MessageRoutes.get_messages, response_model=GetMessagesResponse)
async def get_messages(request: GetMessagesRequest, service: MessageService = Depends(get_message_service), current_user: UserEntity = Depends(get_current_user_depends())):
    if request.user_uuid != current_user.uuid:
        return GetMessagesResponse(success=False, error_message="request.user_uuid != current_user.uuid")

    result = await service.get_messages(request)
    return result
