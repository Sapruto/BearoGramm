from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.modules.user import UserNotFound, get_current_user_depends

from ..models.dto.requests import (
    SendFriendRequest,
    FriendStatusRequest,
)
from ..models.dto.responses import (
    FriendActionResponse,
    GetFriendsResponse,
    GetFriendRequestsResponse,
)
from ..core.exceptions import (
    FriendshipAlreadyExists,
    FriendRequestNotFound,
    FriendRequestAlreadyHandled,
    CannotBeFriendWithSelf,
    CannotAcceptOwnRequest,
    CannotRejectOwnRequest,
    CannotBlockYourself,
    UserAlreadyBlocked,
    UserNotBlocked,
    InvalidTargetIdentifier,
    NotFriends,
)
from ..core.use_cases import FriendUseCases
from ..core.services.friend_service import get_friend_service
from ...chats.chat_types.personal.personal_chat_service import get_personal_chat_service

friend_router = APIRouter(prefix="/api/friends", tags=["friends"])


def get_use_case() -> FriendUseCases:
    return FriendUseCases(friend_protocol=get_friend_service(), personal_protocol=get_personal_chat_service())


@friend_router.post(
    path="/request",
    response_model=FriendActionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_friend_request(
        request: SendFriendRequest,
        current_user=Depends(get_current_user_depends()),
        use_cases: FriendUseCases = Depends(get_use_case),
) -> FriendActionResponse:
    try:
        return await use_cases.send_friend_request(
            from_user_uuid=current_user.uuid,
            request=request,
        )
    except (CannotBeFriendWithSelf, InvalidTargetIdentifier) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FriendshipAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send friend request: {str(e)}",
        )


@friend_router.post(
    path="/status",
    response_model=FriendActionResponse,
)
async def change_friend_status(
        request: FriendStatusRequest,
        current_user=Depends(get_current_user_depends()),
        use_cases: FriendUseCases = Depends(get_use_case),
) -> FriendActionResponse:
    try:
        return await use_cases.change_friend_status(current_user_uuid=current_user.uuid, request=request)
    except CannotBlockYourself as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (CannotAcceptOwnRequest, CannotRejectOwnRequest, NotFriends) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except FriendRequestNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (UserAlreadyBlocked, UserNotBlocked, FriendRequestAlreadyHandled) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change friend status: {str(e)}",
        )


@friend_router.get(
    path="/friends",
    response_model=GetFriendsResponse,
)
async def get_friends(
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        current_user=Depends(get_current_user_depends()),
        use_cases: FriendUseCases = Depends(get_use_case),
) -> GetFriendsResponse:
    try:
        return await use_cases.get_friends(
            user_uuid=current_user.uuid,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get friends: {str(e)}",
        )


@friend_router.get(
    path="/requests",
    response_model=GetFriendRequestsResponse,
)
async def get_friend_requests(
        current_user=Depends(get_current_user_depends()),
        use_cases: FriendUseCases = Depends(get_use_case),
) -> GetFriendRequestsResponse:
    try:
        return await use_cases.get_request_to_friends(current_user.uuid)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get friend requests: {str(e)}",
        )
