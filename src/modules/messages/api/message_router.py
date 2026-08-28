from fastapi import APIRouter, WebSocket, Depends
import json

from src.modules.user import get_current_user_depends, UserEntity, authenticate_by_token
from src.core.logger import get_logger

from .message_router_names import MessageRoutes
from ..core.services.message_service import get_message_service, MessageService
from ..core.services.websocket_message_service import get_websocket_message_service
from ..models.dto.requests import SendMessageRequest, GetMessagesRequest, UpdateMessageRequest, DeleteMessageRequest
from ..models.dto.responses import SendMessageResponse, GetMessagesResponse, UpdateMessageResponse, DeleteMessageResponse

logger = get_logger(__name__)

message_router = APIRouter(prefix=MessageRoutes.base)

@message_router.websocket(MessageRoutes.listen_messages_websocket)
async def listen_messages_websocket(websocket: WebSocket):
    closed = False
    try:
        await websocket.accept()

        ws_service = get_websocket_message_service()

        raw_data = await websocket.receive_text()
        data = json.loads(raw_data)
        token = data.get('auth')

        if not token:
            await websocket.send_text(json.dumps({"error": "Missing auth token"}))
            await websocket.close(code=1008, reason="Missing auth token")
            closed = True
            return
        user = await authenticate_by_token(token)
        if not user:
            await websocket.send_text(json.dumps({"error": "Invalid token"}))
            await websocket.close(code=1008, reason="Invalid token")
            closed = True
            return
        await websocket.send_text(json.dumps({
            "status": "authenticated",
            "user_uuid": user.uuid
        }))

        async def send_message(data: str) -> None:
            await websocket.send_text(data)

        async def receive_message() -> str:
            return await websocket.receive_text()

        await ws_service.listen_messages(
            user_uuid=user.uuid,
            send_message=send_message,
            receive_message=receive_message
        )
    finally:
        if not closed:
            try:
                await websocket.close(code=4000)
            except Exception as e:
                logger.error(f"Error closing websocket: {e}")

@message_router.post(MessageRoutes.send_message, response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest, service: MessageService = Depends(get_message_service), current_user: UserEntity = Depends(get_current_user_depends())):
    if request.user_uuid != current_user.uuid:
        return SendMessageResponse(success=False, error_message="request.user_uuid != current_user.uuid")

    result = await service.send_message(request)
    return result

@message_router.put(MessageRoutes.update_message, response_model=UpdateMessageResponse)
async def update_message(request: UpdateMessageRequest, service: MessageService = Depends(get_message_service), current_user: UserEntity = Depends(get_current_user_depends())):
    if request.user_uuid != current_user.uuid:
        return UpdateMessageResponse(success=False, error_message="request.user_uuid != current_user.uuid")

    return await service.update_message(request)

@message_router.delete(MessageRoutes.delete_message, response_model=DeleteMessageResponse)
async def delete_message(request: DeleteMessageRequest, service: MessageService = Depends(get_message_service), current_user: UserEntity = Depends(get_current_user_depends())):
    if request.user_uuid != current_user.uuid:
        return DeleteMessageResponse(success=False, error_message="request.user_uuid != current_user.uuid")

    return await service.delete_message(request)

@message_router.get(MessageRoutes.get_messages, response_model=GetMessagesResponse)
async def get_messages(request: GetMessagesRequest, service: MessageService = Depends(get_message_service), current_user: UserEntity = Depends(get_current_user_depends())):
    if request.user_uuid != current_user.uuid:
        return GetMessagesResponse(success=False, error_message="request.user_uuid != current_user.uuid")

    result = await service.get_messages(request)
    return result
