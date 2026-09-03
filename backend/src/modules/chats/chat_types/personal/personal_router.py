from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.modules.user import get_current_user_depends

from .personal_chat_service import PersonalChatService, get_personal_chat_service
from .personal_models import (
    PersonalChatResponse,
    PersonalChatCreateRequest,
    PartnerResponse,
    ParticipantCheckResponse,
    DeleteChatResponse,
    PersonalChatListResponse
)
from .personal_exceptions import CannotChatWithSelfError
from ..base.exceptions import (
    UserNotParticipantError,
    PermissionDeniedError,
    ChatNotFoundError,
    InvalidParticipantsError
)


personal_chats_router = APIRouter(prefix="/api/personal")


@personal_chats_router.post(
    path="/create",
    response_model=PersonalChatResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_personal_chat(
        request: PersonalChatCreateRequest,
        current_user = Depends(get_current_user_depends()),
        service: PersonalChatService = Depends(get_personal_chat_service)
) -> PersonalChatResponse:
    try:
        return await service.get_or_create(
            user_uuid=current_user.uuid,
            other_user_uuid=request.other_user_uuid
        )
    except CannotChatWithSelfError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidParticipantsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create personal chat: {str(e)}"
        )


@personal_chats_router.get(
    "/{chat_uuid}",
    response_model=PersonalChatResponse
)
async def get_personal_chat(
        chat_uuid: str,
        current_user = Depends(get_current_user_depends()),
        service: PersonalChatService = Depends(get_personal_chat_service)
) -> PersonalChatResponse:
    try:
        return await service.get_chat(chat_uuid, current_user.uuid)
    except ChatNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserNotParticipantError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat: {str(e)}"
        )


@personal_chats_router.get(
    "/",
    response_model=PersonalChatListResponse
)
async def get_personal_chats(
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        current_user = Depends(get_current_user_depends()),
        service: PersonalChatService = Depends(get_personal_chat_service)
) -> PersonalChatListResponse:
    try:
        chats, total = await service.get_user_chats(
            user_uuid=current_user.uuid,
            limit=limit,
            offset=offset
        )

        return PersonalChatListResponse(
            items=chats,
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chats: {str(e)}"
        )


@personal_chats_router.delete(
    "/{chat_uuid}",
    response_model=DeleteChatResponse
)
async def delete_personal_chat(
        chat_uuid: str,
        current_user = Depends(get_current_user_depends()),
        service: PersonalChatService = Depends(get_personal_chat_service)
) -> DeleteChatResponse:
    try:
        result = await service.delete_chat(chat_uuid, current_user.uuid)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat {chat_uuid} not found"
            )

        return DeleteChatResponse(
            message="Chat deleted successfully",
            chat_uuid=chat_uuid
        )
    except ChatNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserNotParticipantError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat: {str(e)}"
        )


@personal_chats_router.get(
    "/{chat_uuid}/partner",
    response_model=PartnerResponse
)
async def get_chat_partner(
        chat_uuid: str,
        current_user = Depends(get_current_user_depends()),
        service: PersonalChatService = Depends(get_personal_chat_service)
) -> PartnerResponse:
    try:
        partner_uuid = await service.get_chat_partner(chat_uuid, current_user.uuid)
        return PartnerResponse(
            chat_uuid=chat_uuid,
            partner_uuid=partner_uuid
        )
    except ChatNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserNotParticipantError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get partner: {str(e)}"
        )


@personal_chats_router.get(
    "/{chat_uuid}/exists",
    response_model=ParticipantCheckResponse
)
async def check_participant(
        chat_uuid: str,
        current_user= Depends(get_current_user_depends()),
        service: PersonalChatService = Depends(get_personal_chat_service)
) -> ParticipantCheckResponse:
    try:
        is_participant = await service.is_participant(chat_uuid, current_user.uuid)
        return ParticipantCheckResponse(
            chat_uuid=chat_uuid,
            is_participant=is_participant
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check participant: {str(e)}"
        )
