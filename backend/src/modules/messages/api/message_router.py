from fastapi import APIRouter, Depends, HTTPException, status, Path, Query

from src.modules.user import get_current_user_depends, UserEntity
from src.core.logger import get_logger

from .message_router_names import MessageRoutes
from ..core.services.message_service import get_message_service, MessageService
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
        return await service.get_messages(
            chat_uuid=chat_uuid,
            limit=limit,
            offset=offset,
            show_new=show_new,
            user_uuid=current_user.uuid
        )
    except Exception as e:
        logger.error(f"Error in get_messages: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@message_router.get(
    MessageRoutes.get_around_message,
    response_model=GetMessagesResponse,
)
async def get_around_message(
    message_uuid: str = Path(..., description="UUID of target message"),
    span_start: int = Query(default=-10, le=0),
    span_end: int = Query(default=10, ge=0),
    service: MessageService = Depends(get_message_service),
    current_user: UserEntity = Depends(get_current_user_depends()),
):
    try:
        return await service.get_around_message(
            message_uuid=message_uuid,
            user_uuid=current_user.uuid,
            span_start=span_start,
            span_end=span_end,
        )
    except Exception as e:
        logger.error(f"Error in get_around_message: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@message_router.get(
    MessageRoutes.get_messages_before,
    response_model=GetMessagesResponse,
)
async def get_messages_before(
    message_uuid: str = Path(..., description="UUID of the boundary message"),
    limit: int = Query(default=10, ge=1, le=100, description="Count of messages"),
    service: MessageService = Depends(get_message_service),
    current_user: UserEntity = Depends(get_current_user_depends()),
):
    try:
        return await service.get_messages_before(
            before_uuid=message_uuid,
            limit=limit,
            user_uuid=current_user.uuid,
        )
    except Exception as e:
        logger.error(f"Error in get_messages_before: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@message_router.get(
    MessageRoutes.get_messages_after,
    response_model=GetMessagesResponse,
)
async def get_messages_after(
    message_uuid: str = Path(..., description="UUID of the boundary message"),
    limit: int = Query(default=10, ge=1, le=100, description="Count of messages"),
    service: MessageService = Depends(get_message_service),
    current_user: UserEntity = Depends(get_current_user_depends()),
):
    try:
        return await service.get_messages_after(
            after_uuid=message_uuid,
            limit=limit,
            user_uuid=current_user.uuid,
        )
    except Exception as e:
        logger.error(f"Error in get_messages_after: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
