from uuid import uuid4

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from src.modules.user.core.services.verify_service import VerifyService


@pytest.mark.unit
class TestVerifyService:
    @pytest.mark.asyncio
    async def test_send_phone_verify_code_success(self, verify_service, mock_verify_repo, mock_sms_client):
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        mock_verify_repo.delete = AsyncMock(return_value=1)
        mock_verify_repo.save = AsyncMock()

        code = await verify_service.send_phone_verify_code(user_uuid, phone_number)

        assert code == "12345"
        mock_verify_repo.delete.assert_called_once()
        mock_verify_repo.save.assert_called_once()
        mock_sms_client.send_verify_code.assert_called_once_with(
            phone_number=phone_number,
            code="12345",
            time_of_live_per_minuts=5
        )

    @pytest.mark.asyncio
    async def test_send_phone_verify_code_sms_failed(self, verify_service, mock_verify_repo, mock_sms_client):
        mock_sms_client.send_verify_code = AsyncMock(return_value=False)
        mock_verify_repo.delete = AsyncMock(return_value=1)
        mock_verify_repo.save = AsyncMock()
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        code = await verify_service.send_phone_verify_code(user_uuid, phone_number)

        assert code is None
        assert mock_verify_repo.delete.call_count == 2

    @pytest.mark.asyncio
    async def test_send_login_code_success(self, verify_service, mock_verify_repo, mock_sms_client):
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        mock_verify_repo.delete = AsyncMock(return_value=1)
        mock_verify_repo.save = AsyncMock()

        code = await verify_service.send_login_code(user_uuid, phone_number)

        assert code == "12345"
        mock_verify_repo.delete.assert_called_once()
        mock_verify_repo.save.assert_called_once()
        mock_sms_client.send_login_code.assert_called_once_with(
            phone_number=phone_number,
            code="12345",
            time_of_live_per_minuts=5
        )

    @pytest.mark.asyncio
    async def test_send_login_code_sms_failed(self, verify_service, mock_verify_repo, mock_sms_client):
        mock_sms_client.send_login_code = AsyncMock(return_value=False)
        mock_verify_repo.delete = AsyncMock(return_value=1)
        mock_verify_repo.save = AsyncMock()
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        code = await verify_service.send_login_code(user_uuid, phone_number)

        assert code is None
        assert mock_verify_repo.delete.call_count == 2

    @pytest.mark.asyncio
    async def test_send_phone_verify_code_exception(self, verify_service, mock_verify_repo):
        mock_verify_repo.delete = AsyncMock(side_effect=Exception("Redis error"))
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        code = await verify_service.send_phone_verify_code(user_uuid, phone_number)

        assert code is None

    @pytest.mark.asyncio
    async def test_send_login_code_exception(self, verify_service, mock_verify_repo):
        mock_verify_repo.delete = AsyncMock(side_effect=Exception("Redis error"))
        user_uuid = str(uuid4())
        phone_number = "+79001234567"

        code = await verify_service.send_login_code(user_uuid, phone_number)

        assert code is None

    @pytest.mark.asyncio
    async def test_verify_code_valid(self, verify_service, mock_verify_repo):
        code = "12345"

        entity = MagicMock()
        entity.phone = "+79001234567"
        entity.expired_at = datetime.now() + timedelta(minutes=5)

        mock_verify_repo.get = AsyncMock(return_value=entity)
        mock_verify_repo.delete = AsyncMock(return_value=1)

        is_valid = await verify_service.verify_code(code)

        assert is_valid is True
        mock_verify_repo.get.assert_called_once()
        mock_verify_repo.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_code_invalid(self, verify_service, mock_verify_repo):
        mock_verify_repo.get = AsyncMock(return_value=None)

        is_valid = await verify_service.verify_code("invalid_code")

        assert is_valid is False

    @pytest.mark.asyncio
    async def test_verify_code_expired(self, verify_service, mock_verify_repo):
        entity = MagicMock()
        entity.phone = "+79001234567"
        entity.expired_at = datetime.now() - timedelta(minutes=5)

        mock_verify_repo.get = AsyncMock(return_value=entity)
        mock_verify_repo.delete = AsyncMock(return_value=1)

        is_valid = await verify_service.verify_code("12345")

        assert is_valid is False
        mock_verify_repo.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_code_exception(self, verify_service, mock_verify_repo):
        mock_verify_repo.get = AsyncMock(side_effect=Exception("Redis error"))

        is_valid = await verify_service.verify_code("12345")

        assert is_valid is False

    @pytest.mark.asyncio
    async def test_delete_code_success(self, verify_service, mock_verify_repo):
        entity = MagicMock()
        entity.phone = "+79001234567"

        mock_verify_repo.get = AsyncMock(return_value=entity)
        mock_verify_repo.delete = AsyncMock(return_value=1)

        result = await verify_service.delete_code("12345")

        assert result is True
        mock_verify_repo.get.assert_called_once()
        mock_verify_repo.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_code_failed(self, verify_service, mock_verify_repo):
        mock_verify_repo.get = AsyncMock(return_value=None)

        result = await verify_service.delete_code("12345")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_code_exception(self, verify_service, mock_verify_repo):
        mock_verify_repo.get = AsyncMock(side_effect=Exception("Redis error"))

        result = await verify_service.delete_code("12345")

        assert result is False
