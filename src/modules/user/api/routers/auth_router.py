from fastapi import APIRouter, Depends, status
from .auth_route_names import AuthRoutes

from ...models.dto.requests import SendCodeRequest, VerifyCodeRequest
from ...models.dto.responses import SendCodeResponse, VerifyCodeResponse
from ...core.services.user_service import UserService, get_user_service

auth_router = APIRouter(prefix=AuthRoutes.base)


@auth_router.post(
    AuthRoutes.get_login_token,
    response_model=SendCodeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_login_token(
    request: SendCodeRequest, service: UserService = Depends(get_user_service)
):
    return await service.get_login_token_and_register_if_not(request)


@auth_router.post(
    AuthRoutes.verify_phone,
    response_model=VerifyCodeResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_phone(
    request: VerifyCodeRequest, service: UserService = Depends(get_user_service)
):
    return await service.verify_phone(request)
