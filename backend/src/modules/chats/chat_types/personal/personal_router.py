from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.modules.messages.core.services.message_service import get_message_service
from src.modules.profiles_custom.core.services.profile_custom_service import get_profile_custom_service
from src.modules.user import get_current_user_depends

from .personal_chat_service import get_personal_chat_service
from .personal_models import (
    PersonalChatResponse,
    GetChatPartnerResponse,
    DeletePersonalChatResponse,
    GetPersonalChatsResponse,
)
from .personal_exceptions import NotFoundUser
from .use_cases import PersonalUseCases
from ..base.exceptions import (
    UserNotParticipantError,
    PermissionDeniedError,
    ChatNotFoundError
)
from ...core.services.chat_reading_service import get_chat_reading_service
from ...core.services.chat_service import get_chat_service
from ...participants import get_permission_service


personal_chats_router = APIRouter(prefix="/api/personal", tags=["personal_chat"])


def get_use_cases() -> PersonalUseCases:
    return PersonalUseCases(
        personal_protocol=get_personal_chat_service(),
        permission_protocol=get_permission_service(),
        profile_protocol=get_profile_custom_service(),
        chat_reading_protocol=get_chat_reading_service(
            message_service=get_message_service(
                permission_protocol=get_permission_service(),
                chat_protocol=get_chat_service(),
            ),
        ),
    )


@personal_chats_router.get(
    "/{chat_uuid}",
    response_model=PersonalChatResponse
)
async def get_personal_chat(
        chat_uuid: str,
        current_user=Depends(get_current_user_depends()),
        use_cases: PersonalUseCases = Depends(get_use_cases)
) -> PersonalChatResponse:
    try:
        return await use_cases.get_chat(chat_uuid, current_user.uuid)
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
    response_model=GetPersonalChatsResponse
)
async def get_personal_chats(
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        current_user=Depends(get_current_user_depends()),
        use_cases: PersonalUseCases = Depends(get_use_cases)
) -> GetPersonalChatsResponse:
    try:
        chats, total = await use_cases.get_user_personal_chats(
            user_uuid=current_user.uuid,
            limit=limit,
            offset=offset
        )

        return GetPersonalChatsResponse(
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
    response_model=DeletePersonalChatResponse
)
async def delete_personal_chat(
        chat_uuid: str,
        current_user=Depends(get_current_user_depends()),
        use_cases: PersonalUseCases = Depends(get_use_cases)
) -> DeletePersonalChatResponse:
    try:
        result = await use_cases.delete_chat(chat_uuid, current_user.uuid)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat {chat_uuid} not found"
            )

        return DeletePersonalChatResponse(
            message="Chat deleted successfully",
        )
    except NotFoundUser as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to found user: {e}"
        )
    except (UserNotParticipantError, PermissionDeniedError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ChatNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat: {str(e)}"
        )


@personal_chats_router.get(
    "/{chat_uuid}/partner",
    response_model=GetChatPartnerResponse
)
async def get_chat_partner(
        chat_uuid: str,
        current_user=Depends(get_current_user_depends()),
        use_cases: PersonalUseCases = Depends(get_use_cases)
) -> GetChatPartnerResponse:
    try:
        return await use_cases.get_chat_partner(chat_uuid, current_user.uuid)
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
