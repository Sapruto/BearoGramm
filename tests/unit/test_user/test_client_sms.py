import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.modules.user.core.client.client_sms_api import ClientSMS
from src.modules.user.core.client.client_sms_ru import ClientSMSRu


@pytest.mark.unit
class TestClientSMS:
    @pytest.mark.asyncio
    async def test_send_verify_code(self, mock_sms_client):
        result = await mock_sms_client.send_verify_code(
            phone_number="+79001234567", code="123456", time_of_live_per_minuts=5
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_send_login_code(self, mock_sms_client):
        result = await mock_sms_client.send_login_code(
            phone_number="+79001234567", code="123456", time_of_live_per_minuts=5
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_send_custom_sms(self, mock_sms_client):
        result = await mock_sms_client.send_custom_sms(
            phone_number="+79001234567", message="Test message"
        )
        assert result is True


@pytest.mark.unit
class TestClientSMSRu:
    @patch("src.modules.user.core.client.client_sms_ru.Settings")
    @patch("src.modules.user.core.client.client_sms_ru.AsyncClient")
    def test_client_initialization(self, mock_async_client, mock_settings):
        mock_settings.PHONE.ASYNC_CLIENT_API_ID = "test_key"
        mock_async_client.return_value = MagicMock()
        client = ClientSMSRu()
        assert client.api_key == "test_key"
        assert client._client is not None

    @patch.dict("os.environ", {})
    @patch("src.modules.user.core.client.client_sms_ru.Settings")
    def test_client_initialization_no_key(self, mock_settings):
        mock_settings.PHONE.ASYNC_CLIENT_API_ID = None
        with pytest.raises(ValueError) as exc:
            ClientSMSRu()
        assert "ASYNC_CLIENT_API_ID" in str(exc.value)

    @pytest.mark.asyncio
    @patch("src.modules.user.core.client.client_sms_ru.Settings")
    @patch("src.modules.user.core.client.client_sms_ru.AsyncClient")
    async def test_send_sms_success(self, mock_async_client, mock_settings):
        mock_settings.PHONE.ASYNC_CLIENT_API_ID = "test_key"
        mock_client = MagicMock()
        mock_client.send = AsyncMock(return_value={"status": "OK"})
        mock_async_client.return_value = mock_client
        client = ClientSMSRu()
        result = await client.send_sms("+79001234567", "Test message")
        assert result is True

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"SMS_RU_API_KEY": "test_key"})
    @patch("src.modules.user.core.client.client_sms_ru.AsyncClient")
    async def test_send_sms_failed(self, mock_async_client):
        mock_client = MagicMock()
        mock_client.send = AsyncMock(return_value={"status": "ERROR"})
        mock_async_client.return_value = mock_client
        client = ClientSMSRu(max_retries=1)
        result = await client.send_sms("+79001234567", "Test message")
        assert result is False

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"SMS_RU_API_KEY": "test_key"})
    @patch("src.modules.user.core.client.client_sms_ru.AsyncClient")
    async def test_send_sms_exception(self, mock_async_client):
        mock_client = MagicMock()
        mock_client.send = AsyncMock(side_effect=Exception("Network error"))
        mock_async_client.return_value = mock_client
        client = ClientSMSRu(max_retries=1)
        result = await client.send_sms("+79001234567", "Test message")
        assert result is False
