from fastapi import APIRouter

from .auth_route_names import AuthRoutes

from ...models.dto.requests import SendCodeRequest, VerifyCodeRequest
from ...models.dto.responses import SendCodeResponse, VerifyCodeResponse
from ...core.services.user_service import UserService, get_user_service

from src.core.logger import get_logger

logger = get_logger(__name__)

auth_router = APIRouter()

@auth_router.post(AuthRoutes.get_login_token)
async def get_login_token(request: SendCodeRequest) -> SendCodeResponse:
    service = get_user_service()
    return await service.get_login_token_and_register_if_not(request)

@auth_router.post(AuthRoutes.verify_phone)
async def verify_phone(request: VerifyCodeRequest) -> VerifyCodeResponse:
    service = get_user_service()
    return await service.verify_phone(request)
