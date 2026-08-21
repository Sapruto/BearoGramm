from functools import wraps
from typing import Any, Optional, Callable, TypeVar
from fastapi import Request

from src.modules.sessions import SessionAPIService, get_session_service_api
from src.core.logger import get_logger

from ..imports.user_service_api import get_user_service_api
from ..exceptions import UserHaveNotAccess, UserNotFound

logger = get_logger(__name__)

T = TypeVar('T')

def login_required(session_service: Optional[SessionAPIService] = None):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                request = kwargs.get('request')

            if not request:
                raise UserHaveNotAccess("Request object not found")

            token = request.headers.get("Authorization")
            if not token:
                raise UserHaveNotAccess("Authorization header missing")

            if token.startswith("Bearer "):
                token = token[7:]

            session_svc = session_service or get_session_service_api()
            session = await session_svc.validate_session(token)

            if not session.is_valid:
                raise UserHaveNotAccess("Invalid or expired session token")

            request.state.user_uuid = session.user_uuid

            return await func(*args, **kwargs)

        return wrapper

    return decorator

async def get_current_user_uuid(request: Request) -> str:
    user_uuid = getattr(request.state, 'user_uuid', None)
    if not user_uuid:
        raise UserHaveNotAccess("User not authenticated")
    return user_uuid

async def get_current_user(request: Request, user_api_service=None) -> Any:
    user_uuid = await get_current_user_uuid(request)

    if not user_api_service:
        user_api_service = get_user_service_api()

    user = await user_api_service.get_user_by_uuid(user_uuid)
    if not user:
        raise UserNotFound("User not found")

    return user
