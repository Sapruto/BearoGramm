from fastapi import APIRouter, WebSocket, Depends, HTTPException, status, Path, Query
import json

from src.modules.user import get_current_user_depends, UserEntity, authenticate_by_token
from src.core.logger import get_logger

from .message_router_names import MessageRoutes
from ..core.services.message_service import get_message_service, MessageService
from ..core.services.websocket_message_service import get_websocket_message_service
from ..models.dto.requests import (
    SendMessageRequest,
    UpdateMessageRequest,
)
from ..models.dto.responses import (
    SendMessageResponse,
    GetMessagesResponse,
    UpdateMessageResponse,
    DeleteMessageResponse,
)

logger = get_logger(__name__)

message_router = APIRouter(prefix=MessageRoutes.base, tags=["messages"])


@message_router.websocket(MessageRoutes.listen_messages_websocket)
async def listen_messages_websocket(websocket: WebSocket):
    closed = False
    try:
        await websocket.accept()

        ws_service = get_websocket_message_service()

        raw_data = await websocket.receive_text()
        data = json.loads(raw_data)
        token = data.get("auth")

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
        await websocket.send_text(
            json.dumps({"status": "authenticated", "user_uuid": user.uuid})
        )

        async def send_message(data: str) -> None:
            await websocket.send_text(data)

        async def receive_message() -> str:
            return await websocket.receive_text()

        await ws_service.listen_messages(
            user_uuid=user.uuid,
            send_message=send_message,
            receive_message=receive_message,
        )
    finally:
        if not closed:
            try:
                await websocket.close(code=4000)
            except Exception as e:
                logger.error(f"Error closing websocket: {e}")

@message_router.post(MessageRoutes.send_message, response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    service: MessageService = Depends(get_message_service),
    current_user: UserEntity = Depends(get_current_user_depends()),
):
    try:
        return await service.send_message(request, current_user.uuid)
    except Exception as e:
        logger.error(f"Error in send_message: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@message_router.put(MessageRoutes.update_message, response_model=UpdateMessageResponse)
async def update_message(
    request: UpdateMessageRequest,
    service: MessageService = Depends(get_message_service),
    current_user: UserEntity = Depends(get_current_user_depends()),
):
    try:
        return await service.update_message(request, current_user.uuid)
    except Exception as e:
        logger.error(f"Error in update_message: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@message_router.delete(MessageRoutes.delete_message, response_model=DeleteMessageResponse)
async def delete_message(
    message_uuid: str = Path(..., description="UUID of message"),
    service: MessageService = Depends(get_message_service),
    current_user: UserEntity = Depends(get_current_user_depends()),
):
    try:
        return await service.delete_message(message_uuid, current_user.uuid)
    except Exception as e:
        logger.error(f"Error in delete_message: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@message_router.get(MessageRoutes.get_messages + "/{chat_uuid}", response_model=GetMessagesResponse)
async def get_messages(
    chat_uuid: str = Path(..., description="UUID of chat"),
    limit: int = Query(default=10, ge=1, le=100, description="Count of Message"),
    offset: int = Query(default=0, ge=0, description="Offset"),
    show_new: bool = Query(
        default=True,
        description="If this = false, we must show a f*cking old messages else new",
    ),
    service: MessageService = Depends(get_message_service),
    current_user: UserEntity = Depends(get_current_user_depends()),
):
    try:
        return await service.get_messages(chat_uuid=chat_uuid,
            limit=limit,
            offset=offset,
            show_new=show_new,
            user_uuid=current_user.uuid
        )
    except Exception as e:
        logger.error(f"Error in get_messages: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
