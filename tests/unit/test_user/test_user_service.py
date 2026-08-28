from unittest.mock import AsyncMock
import pytest
from uuid import uuid4

from src.modules.user.core.services.user_service import UserService
from src.modules.user.models.entities.user_entity import UserEntity
from src.modules.user.models.dto.requests import SendCodeRequest, VerifyCodeRequest


@pytest.mark.unit
class TestUserService:
    @pytest.mark.asyncio
    async def test_get_login_token_new_user(self, user_service, user_repository, verify_service):
        request = SendCodeRequest(phone_number="+79001234567")

        user_repository.get_by_field = AsyncMock(return_value=None)
        new_user = UserEntity(phone_number="+79001234567")
        user_repository.save = AsyncMock(return_value=new_user)
        verify_service.send_login_code = AsyncMock(return_value="test_token_123456")

        response = await user_service.get_login_token_and_register_if_not(request)

        assert response.success is True
        assert response.error_message is None
        user_repository.save.assert_called_once()
        verify_service.send_login_code.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_login_token_existing_user(self, user_service, user_repository, verify_service):
        request = SendCodeRequest(phone_number="+79001234567")
        existing_user = UserEntity(
            uuid=str(uuid4()),
            phone_number="+79001234567"
        )

        user_repository.get_by_field = AsyncMock(return_value=existing_user)
        verify_service.send_login_code = AsyncMock(return_value="test_token_123456")

        response = await user_service.get_login_token_and_register_if_not(request)

        assert response.success is True
        user_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_login_token_failed_to_create_user(self, user_service, user_repository):
        request = SendCodeRequest(phone_number="+79001234567")

        user_repository.get_by_field = AsyncMock(return_value=None)
        user_repository.save = AsyncMock(return_value=None)

        response = await user_service.get_login_token_and_register_if_not(request)

        assert response.success is False
        assert response.error_message == "Failed to create user"

    @pytest.mark.asyncio
    async def test_get_login_token_failed_to_send_code(self, user_service, user_repository, verify_service):
        request = SendCodeRequest(phone_number="+79001234567")
        new_user = UserEntity(phone_number="+79001234567")

        user_repository.get_by_field = AsyncMock(return_value=None)
        user_repository.save = AsyncMock(return_value=new_user)
        verify_service.send_login_code = AsyncMock(return_value=None)

        response = await user_service.get_login_token_and_register_if_not(request)

        assert response.success is False
        assert response.error_message == "Failed to send code"

    @pytest.mark.asyncio
    async def test_get_login_token_exception(self, user_service, user_repository):
        request = SendCodeRequest(phone_number="+79001234567")
        user_repository.get_by_field = AsyncMock(side_effect=Exception("DB error"))

        response = await user_service.get_login_token_and_register_if_not(request)

        assert response.success is False
        assert response.error_message == "Failed to get login token"

    @pytest.mark.asyncio
    async def test_verify_phone_success(self, user_service, verify_service, user_repository):
        request = VerifyCodeRequest(
            phone_number="+79001234567",
            code="123456"
        )
        user = UserEntity(
            uuid=str(uuid4()),
            phone_number="+79001234567"
        )

        verify_service.verify_code = AsyncMock(return_value=True)
        user_repository.get_by_field = AsyncMock(return_value=user)
        user_repository.save = AsyncMock(return_value=user)
        verify_service.delete_code = AsyncMock(return_value=True)

        response = await user_service.verify_phone(request)

        assert response.success is True
        assert response.user == user
        assert response.error_message is None
        user_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_phone_invalid_code(self, user_service, verify_service):
        request = VerifyCodeRequest(
            phone_number="+79001234567",
            code="123456"
        )

        verify_service.verify_code = AsyncMock(return_value=False)

        response = await user_service.verify_phone(request)

        assert response.success is False
        assert response.error_message == "Invalid or expired code"
        assert response.user is None

    @pytest.mark.asyncio
    async def test_verify_phone_user_not_found(self, user_service, verify_service, user_repository):
        request = VerifyCodeRequest(
            phone_number="+79001234567",
            code="123456"
        )

        verify_service.verify_code = AsyncMock(return_value=True)
        user_repository.get_by_field = AsyncMock(return_value=None)

        response = await user_service.verify_phone(request)

        assert response.success is False
        assert response.error_message == "User not found"

    @pytest.mark.asyncio
    async def test_verify_phone_exception(self, user_service, verify_service):
        request = VerifyCodeRequest(
            phone_number="+79001234567",
            code="123456"
        )

        verify_service.verify_code = AsyncMock(side_effect=Exception("Validation error"))

        response = await user_service.verify_phone(request)

        assert response.success is False
        assert response.error_message == "Verification failed"
