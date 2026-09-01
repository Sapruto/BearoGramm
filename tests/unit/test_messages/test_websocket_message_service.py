import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.modules.messages.core.services.websocket_message_service import (
    WebSocketMessageService,
    get_websocket_message_service,
)


@pytest.mark.unit
class TestWebSocketMessageService:
    @pytest.fixture
    def mock_state_repo(self):
        repo = MagicMock()
        repo.set_user_online = AsyncMock(return_value=True)
        repo.set_user_offline = AsyncMock(return_value=True)
        repo.publish_notification = AsyncMock()
        repo.publish_to_chat = AsyncMock()
        repo.get_notification_channel = AsyncMock(
            return_value="user:notifications:test"
        )
        repo.redis = MagicMock()
        repo.redis.pubsub = MagicMock()
        return repo

    @pytest.fixture
    def service(self, mock_state_repo):
        return WebSocketMessageService(
            state_repository=mock_state_repo, time_of_expire_per_seconds=3600
        )

    @pytest.mark.asyncio
    async def test_connect(self, service, mock_state_repo):
        result = await service.connect("test_uuid")

        assert result is True
        mock_state_repo.set_user_online.assert_called_once_with("test_uuid")

    @pytest.mark.asyncio
    async def test_disconnect(self, service, mock_state_repo):
        result = await service.disconnect("test_uuid")

        assert result is True
        mock_state_repo.set_user_offline.assert_called_once_with("test_uuid")

    @pytest.mark.asyncio
    async def test_notify_user(self, service, mock_state_repo):
        notification = {"type": "test"}
        await service.notify_user("test_uuid", notification)

        mock_state_repo.publish_notification.assert_called_once_with(
            "test_uuid", notification
        )

    @pytest.mark.asyncio
    async def test_notify_chat_participants(self, service, mock_state_repo):
        notification = {"type": "test"}
        await service.notify_chat_participants("chat_uuid", notification)

        mock_state_repo.publish_to_chat.assert_called_once_with(
            "chat_uuid", notification
        )

    @pytest.mark.asyncio
    async def test_parse_websocket_data_writing(self, service, mock_state_repo):
        data = json.dumps({"type": "writing", "chat_uuid": "chat_123"})
        send_message = AsyncMock()

        await service._parse_websocket_data(data, "user_uuid", send_message)

        mock_state_repo.publish_to_chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_parse_websocket_data_ping(self, service, mock_state_repo):
        data = json.dumps({"type": "ping"})
        send_message = AsyncMock()

        await service._parse_websocket_data(data, "user_uuid", send_message)

        send_message.assert_called_once_with(json.dumps({"type": "pong"}))

    @pytest.mark.asyncio
    async def test_parse_websocket_data_invalid_json(self, service, mock_state_repo):
        data = "invalid json"
        send_message = AsyncMock()

        await service._parse_websocket_data(data, "user_uuid", send_message)

        mock_state_repo.publish_to_chat.assert_not_called()
        send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_parse_websocket_data_unknown_type(self, service, mock_state_repo):
        data = json.dumps({"type": "unknown"})
        send_message = AsyncMock()

        await service._parse_websocket_data(data, "user_uuid", send_message)

        mock_state_repo.publish_to_chat.assert_not_called()
        send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_listen_messages(self, service, mock_state_repo):
        send_message = AsyncMock()
        receive_message = AsyncMock()
        receive_message.side_effect = [
            json.dumps({"type": "ping"}),
            Exception("Closed"),
        ]

        mock_pubsub = MagicMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.listen = AsyncMock(return_value=iter([]))
        mock_pubsub.unsubscribe = AsyncMock()
        mock_state_repo.redis.pubsub.return_value = mock_pubsub

        with patch("asyncio.create_task") as mock_create_task:
            mock_task = MagicMock()
            mock_task.done = MagicMock(return_value=True)
            mock_create_task.return_value = mock_task

            await service.listen_messages("user_uuid", send_message, receive_message)

    def test_get_websocket_message_service(self):
        service = get_websocket_message_service()
        assert isinstance(service, WebSocketMessageService)
