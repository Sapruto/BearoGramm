import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.modules.calls.core.clients.push_client_api import PushClientAPI, get_push_client_api
from src.modules.calls.core.clients.push_client_impl import PushClientImpl


@pytest.mark.unit
class TestPushClientAPI:
    @pytest.fixture
    def push_client_api(self, mock_push_impl):
        with patch('src.modules.calls.core.clients.push_client_api.get_push_impl', return_value=mock_push_impl):
            return PushClientAPI()

    @pytest.mark.asyncio
    async def test_send_push_notification_success(self, push_client_api, mock_push_impl):
        result = await push_client_api.send_push_notification(
            phone_number="+79001234567",
            title="Test Title",
            body="Test Body",
            data={"key": "value"}
        )

        assert result is True
        mock_push_impl.send.assert_called_once_with(
            phone_number="+79001234567",
            title="Test Title",
            body="Test Body",
            data={"key": "value", "type": "incoming_call_push"}
        )

    @pytest.mark.asyncio
    async def test_send_push_notification_no_data(self, push_client_api, mock_push_impl):
        result = await push_client_api.send_push_notification(
            phone_number="+79001234567"
        )

        assert result is True
        mock_push_impl.send.assert_called_once()
        call_kwargs = mock_push_impl.send.call_args[1]
        assert call_kwargs["data"] == {"type": "incoming_call_push"}

    @pytest.mark.asyncio
    async def test_send_push_notification_failed(self, push_client_api, mock_push_impl):
        mock_push_impl.send = AsyncMock(return_value=False)

        result = await push_client_api.send_push_notification(
            phone_number="+79001234567"
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_send_push_notification_exception(self, push_client_api, mock_push_impl):
        mock_push_impl.send = AsyncMock(side_effect=Exception("Push error"))

        result = await push_client_api.send_push_notification(
            phone_number="+79001234567"
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_send_call_push(self, push_client_api):
        push_client_api.send_push_notification = AsyncMock(return_value=True)

        result = await push_client_api.send_call_push(
            phone_number="+79001234567",
            caller_uuid="caller_uuid",
            caller_name="Test User",
            room_id="room_123"
        )

        assert result is True
        push_client_api.send_push_notification.assert_called_once_with(
            phone_number="+79001234567",
            title="Test User звонит",
            body="Нажмите, чтобы ответить",
            data={"caller_uuid": "caller_uuid", "room_id": "room_123"}
        )

    @pytest.mark.asyncio
    async def test_send_call_push_default_name(self, push_client_api):
        push_client_api.send_push_notification = AsyncMock(return_value=True)

        result = await push_client_api.send_call_push(
            phone_number="+79001234567",
            caller_uuid="caller_uuid"
        )

        assert result is True
        push_client_api.send_push_notification.assert_called_once_with(
            phone_number="+79001234567",
            title="caller_name звонит",
            body="Нажмите, чтобы ответить",
            data={"caller_uuid": "caller_uuid", "room_id": None}
        )

    def test_get_push_client_api(self):
        client = get_push_client_api()
        assert isinstance(client, PushClientAPI)
