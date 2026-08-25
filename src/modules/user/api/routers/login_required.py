from functools import wraps
from typing import Optional, Callable, TypeVar
from fastapi import Request, HTTPException, status, WebSocket

from src.modules.sessions import SessionAPIService, get_session_service_api
from src.core.logger import get_logger

from ..imports.user_service_api import get_user_service_api
from ...models.entities.user_entity import UserEntity

logger = get_logger(__name__)

T = TypeVar('T')

def get_request_from_args(*args, **kwargs) -> Optional[Request]:
    for arg in args:
        if isinstance(arg, Request):
            return arg
    return kwargs.get('request')

async def get_current_user(request: Request, session_service: Optional[SessionAPIService] = None, user_service=None) -> UserEntity:
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    if token.startswith("Bearer "):
        token = token[7:]

    session_svc = session_service or get_session_service_api()
    session = await session_svc.validate_session(token)

    if not session.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )

    user_svc = user_service or get_user_service_api()
    user = await user_svc.get_user_by_uuid(session.user_uuid)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

def login_required(session_service: Optional[SessionAPIService] = None):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = get_request_from_args(*args, **kwargs)
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )

            token = request.headers.get("Authorization")
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header missing"
                )

            if token.startswith("Bearer "):
                token = token[7:]

            session_svc = session_service or get_session_service_api()
            session = await session_svc.validate_session(token)

            if not session.is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired session token"
                )

            user_svc = get_user_service_api()
            user = await user_svc.get_user_by_uuid(session.user_uuid)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            kwargs['current_user'] = user
            request.state.user = user

            return await func(*args, **kwargs)

        return wrapper

    return decorator

def get_current_user_depends(session_service: Optional[SessionAPIService] = None, user_service = None):
    async def _get_current_user(request: Request) -> UserEntity:
        return await get_current_user(request, session_service, user_service)

    return _get_current_user


async def get_user_in_websocket(websocket: WebSocket, user_uuid: str = None, token: str = None, session_service: Optional[SessionAPIService] = None) -> Optional[UserEntity]:
    user_svc = get_user_service_api()
    session_svc = session_service or get_session_service_api()

    if user_uuid:
        try:
            user = await user_svc.get_user_by_uuid(user_uuid)
            if user:
                return user
        except Exception as e:
            logger.error(f"Error getting user by uuid: {e}")

    if token:
        try:
            if token.startswith("Bearer "):
                token = token[7:]

            session = await session_svc.validate_session(token)
            if session and session.is_valid:
                user = await user_svc.get_user_by_uuid(session.user_uuid)
                if user:
                    return user
        except Exception as e:
            logger.error(f"Error validating token: {e}")

    if not token:
        token = websocket.query_params.get("token")
        if token:
            return await get_user_in_websocket(websocket, None, token, session_service)

    return None
