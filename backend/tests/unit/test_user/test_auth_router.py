import pytest
from unittest.mock import AsyncMock

from src.modules.user.api.routers.auth_router import (
    auth_router,
    get_login_token,
    verify_phone,
)
from src.modules.user.models.dto.requests import SendCodeRequest, VerifyCodeRequest
from src.modules.user.models.dto.responses import SendCodeResponse, VerifyCodeResponse
from src.modules.user.models.entities.user_entity import UserEntity


@pytest.mark.unit
class TestAuthRouter:
    @pytest.mark.asyncio
    async def test_get_login_token(self):
        request = SendCodeRequest(phone_number="+79001234567")
        mock_service = AsyncMock()
        mock_service.get_login_token_and_register_if_not = AsyncMock(
            return_value=SendCodeResponse(success=True)
        )

        response = await get_login_token(request, mock_service)

        assert response.success is True
        mock_service.get_login_token_and_register_if_not.assert_called_once_with(
            request
        )

    def test_router_prefix(self):
        assert auth_router.prefix == "/api/auth"

    def test_router_routes(self):
        routes = [route.path for route in auth_router.routes]
        assert "/api/auth/get_login_token" in routes
        assert "/api/auth/verify_phone" in routes
