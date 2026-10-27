from .api.exports.user_service import UserService, get_user_service
from .api.exports.models import (
    UserSessionsAPIModel,
    UserSessionResponseAPIModel,
)
from .api.routers.auth_route_names import AuthRoutes, AuthRoutesURL
from .api.routers.auth_router import auth_router
from .api.routers.login_required import (
    login_required,
    get_current_user_depends,
    get_current_user,
    authenticate_by_token,
)

from .core.exceptions import UserNotFound

from .models.entities.user_entity import UserEntity

__all__ = [
    "UserService",
    "get_user_service",
    "UserSessionsAPIModel",
    "UserSessionResponseAPIModel",
    "auth_router",
    "AuthRoutes",
    "AuthRoutesURL",
    "login_required",
    "get_current_user_depends",
    "get_current_user",
    "authenticate_by_token",
    "UserEntity",
    "UserNotFound",
]
