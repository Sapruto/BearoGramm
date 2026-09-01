import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, Request

from src.modules.user.api.routers.login_required import (
    login_required,
    get_current_user,
    get_current_user_depends,
    authenticate_by_token,
)
from src.modules.user.models.entities.user_entity import UserEntity


@pytest.mark.unit
class TestLoginRequired:
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_request, mock_session_service):
        user = UserEntity(uuid="test_uuid", phone_number="+79001234567")
        mock_user_service = AsyncMock()
        mock_user_service.get_user_by_uuid = AsyncMock(return_value=user)

        result = await get_current_user(
            mock_request, mock_session_service, mock_user_service
        )

        assert result == user
        mock_session_service.validate_session.assert_called_once()
        mock_user_service.get_user_by_uuid.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, mock_session_service):
        request = MagicMock()
        request.headers = {}

        with pytest.raises(HTTPException) as exc:
            await get_current_user(request, mock_session_service)

        assert exc.value.status_code == 401
        assert "Authorization header missing" in str(exc.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(
        self, mock_request, mock_session_service
    ):
        validate_response = MagicMock()
        validate_response.is_valid = False
        mock_session_service.validate_session = AsyncMock(
            return_value=validate_response
        )

        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_request, mock_session_service)

        assert exc.value.status_code == 401
        assert "Invalid or expired session token" in str(exc.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(
        self, mock_request, mock_session_service
    ):
        mock_user_service = AsyncMock()
        mock_user_service.get_user_by_uuid = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await get_current_user(
                mock_request, mock_session_service, mock_user_service
            )

        assert exc.value.status_code == 404
        assert "User not found" in str(exc.value.detail)

    @pytest.mark.asyncio
    async def test_login_required_no_request(self, mock_session_service):
        @login_required(mock_session_service)
        async def test_endpoint():
            return "ok"

        with pytest.raises(HTTPException) as exc:
            await test_endpoint()

        assert exc.value.status_code == 500
        assert "Request object not found" in str(exc.value.detail)

    @pytest.mark.asyncio
    async def test_login_required_no_auth_header(self, mock_session_service):
        request = MagicMock()
        request.headers = {}

        @login_required(mock_session_service)
        async def test_endpoint(request: Request):
            return "ok"

        with pytest.raises(HTTPException) as exc:
            await test_endpoint(request=request)

        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_depends(self, mock_request, mock_session_service):
        mock_user = UserEntity(uuid="test_uuid", phone_number="+79001234567")
        mock_user_service = AsyncMock()
        mock_user_service.get_user_by_uuid = AsyncMock(return_value=mock_user)

        depends = get_current_user_depends(mock_session_service, mock_user_service)
        result = await depends(mock_request)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_authenticate_by_token_success(self):
        mock_user = UserEntity(uuid="test_uuid", phone_number="+79001234567")
        mock_session_service = AsyncMock()
        validate_response = MagicMock()
        validate_response.is_valid = True
        validate_response.user_uuid = "test_uuid"
        mock_session_service.validate_session = AsyncMock(
            return_value=validate_response
        )

        mock_user_service = AsyncMock()
        mock_user_service.get_user_by_uuid = AsyncMock(return_value=mock_user)

        with patch(
            "src.modules.user.api.routers.login_required.get_session_service_api",
            return_value=mock_session_service,
        ):
            with patch(
                "src.modules.user.api.routers.login_required.get_user_service_api",
                return_value=mock_user_service,
            ):
                result = await authenticate_by_token("Bearer test_token")

                assert result == mock_user

    @pytest.mark.asyncio
    async def test_authenticate_by_token_invalid(self):
        mock_session_service = AsyncMock()
        validate_response = MagicMock()
        validate_response.is_valid = False
        mock_session_service.validate_session = AsyncMock(
            return_value=validate_response
        )

        with patch(
            "src.modules.user.api.routers.login_required.get_session_service_api",
            return_value=mock_session_service,
        ):
            result = await authenticate_by_token("Bearer test_token")

            assert result is None
