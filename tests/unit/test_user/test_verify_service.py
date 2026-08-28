from uuid import uuid4

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from src.modules.user.core.services.verify_service import VerifyService
from src.modules.sessions.api.models import CreateSessionRequest


@pytest.mark.unit
class TestVerifyService:
    @pytest.mark.asyncio
    async def test_send_phone_verify_code_success(self, verify_service, mock_session_service, mock_sms_client):
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        code = await verify_service.send_phone_verify_code(user_uuid, phone_number)

        assert code == "test_token_123456"
        mock_session_service.create_session.assert_called_once_with(
            request=CreateSessionRequest(user_uuid=user_uuid)
        )
        mock_sms_client.send_verify_code.assert_called_once_with(
            phone_number=phone_number,
            code="test_token_123456",
            time_of_live_per_minuts=5
        )

    @pytest.mark.asyncio
    async def test_send_phone_verify_code_sms_failed(self, verify_service, mock_session_service, mock_sms_client):
        mock_sms_client.send_verify_code = AsyncMock(return_value=False)
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        code = await verify_service.send_phone_verify_code(user_uuid, phone_number)

        assert code is None
        mock_session_service.create_session.assert_called_once()
        mock_session_service.delete_session.assert_called_once_with("test_token_123456")

    @pytest.mark.asyncio
    async def test_send_login_code_success(self, verify_service, mock_session_service, mock_sms_client):
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        code = await verify_service.send_login_code(user_uuid, phone_number)

        assert code == "test_token_123456"
        mock_session_service.create_session.assert_called_once()
        mock_sms_client.send_login_code.assert_called_once_with(
            phone_number=phone_number,
            code="test_token_123456",
            time_of_live_per_minuts=5
        )

    @pytest.mark.asyncio
    async def test_send_login_code_sms_failed(self, verify_service, mock_session_service, mock_sms_client):
        mock_sms_client.send_login_code = AsyncMock(return_value=False)
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        code = await verify_service.send_login_code(user_uuid, phone_number)

        assert code is None
        mock_session_service.delete_session.assert_called_once_with("test_token_123456")

    @pytest.mark.asyncio
    async def test_send_phone_verify_code_exception(self, verify_service, mock_session_service):
        mock_session_service.create_session = AsyncMock(side_effect=Exception("Session error"))
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        code = await verify_service.send_phone_verify_code(user_uuid, phone_number)

        assert code is None

    @pytest.mark.asyncio
    async def test_send_login_code_exception(self, verify_service, mock_session_service):
        mock_session_service.create_session = AsyncMock(side_effect=Exception("Session error"))
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        code = await verify_service.send_login_code(user_uuid, phone_number)

        assert code is None

    @pytest.mark.asyncio
    async def test_verify_code_valid(self, verify_service, mock_session_service):
        code = "test_token_123456"
        is_valid = await verify_service.verify_code(code)

        assert is_valid is True
        mock_session_service.validate_session.assert_called_once_with(code)

    @pytest.mark.asyncio
    async def test_verify_code_invalid(self, verify_service, mock_session_service):
        session_response = MagicMock()
        session_response.is_valid = False
        mock_session_service.validate_session = AsyncMock(return_value=session_response)

        is_valid = await verify_service.verify_code("invalid_token")

        assert is_valid is False

    @pytest.mark.asyncio
    async def test_verify_code_exception(self, verify_service, mock_session_service):
        mock_session_service.validate_session = AsyncMock(side_effect=Exception("DB error"))

        is_valid = await verify_service.verify_code("test_token")

        assert is_valid is False

    @pytest.mark.asyncio
    async def test_delete_code_success(self, verify_service, mock_session_service):
        result = await verify_service.delete_code("test_token")

        assert result is True
        mock_session_service.delete_session.assert_called_once_with("test_token")

    @pytest.mark.asyncio
    async def test_delete_code_failed(self, verify_service, mock_session_service):
        mock_session_service.delete_session = AsyncMock(return_value=MagicMock(success=False))

        result = await verify_service.delete_code("test_token")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_code_exception(self, verify_service, mock_session_service):
        mock_session_service.delete_session = AsyncMock(side_effect=Exception("Delete error"))

        result = await verify_service.delete_code("test_token")

        assert result is False
