from fastapi import APIRouter, Depends, HTTPException, Query, status

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
from ..core.services.friend_service import FriendService, get_friend_service
from src.modules.user import UserNotFound, get_current_user_depends


friend_router = APIRouter(prefix="/api/friends", tags=["friends"])


@friend_router.post(
    path="/request",
    response_model=FriendActionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_friend_request(
        request: SendFriendRequest,
        current_user = Depends(get_current_user_depends()),
        service: FriendService = Depends(get_friend_service),
) -> FriendActionResponse:
    try:
        return await service.send_friend_request(
            from_user_uuid=current_user.uuid,
            request=request,
        )
    except CannotBeFriendWithSelf as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InvalidTargetIdentifier as e:
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
        current_user = Depends(get_current_user_depends()),
        service: FriendService = Depends(get_friend_service),
) -> FriendActionResponse:
    try:
        return await service.change_status(
            current_user_uuid=current_user.uuid,
            request=request,
        )
    except CannotAcceptOwnRequest as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except CannotRejectOwnRequest as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except CannotBlockYourself as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserAlreadyBlocked as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except UserNotBlocked as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except FriendRequestAlreadyHandled as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except FriendRequestNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotFriends as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
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
        current_user = Depends(get_current_user_depends()),
        service: FriendService = Depends(get_friend_service),
) -> GetFriendsResponse:
    try:
        return await service.get_friends(
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
        current_user = Depends(get_current_user_depends()),
        service: FriendService = Depends(get_friend_service),
) -> GetFriendRequestsResponse:
    try:
        return await service.get_request_to_friends(current_user.uuid)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get friend requests: {str(e)}",
        )
