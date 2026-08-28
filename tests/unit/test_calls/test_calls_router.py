from uuid import uuid4

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import asyncio

from src.modules.calls.api.calls_router import calls_router
from src.modules.calls.api.calls_router_names import CallsRoutes


@pytest.mark.unit
class TestCallsRouter:
    def test_router_prefix(self):
        assert calls_router.prefix == "/api/calls"

    @pytest.mark.asyncio
    async def test_call_websocket_missing_token(self):
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(return_value=json.dumps({}))
        mock_websocket.send_text = AsyncMock()
        mock_websocket.close = AsyncMock()

        with patch('src.modules.calls.api.calls_router.authenticate_by_token', return_value=None):
            from src.modules.calls.api.calls_router import call
            await call(mock_websocket)

            mock_websocket.send_text.assert_called_with(json.dumps({"error": "Missing auth token"}))

    @pytest.mark.asyncio
    async def test_call_websocket_invalid_token(self):
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(return_value=json.dumps({"auth": "invalid_token"}))
        mock_websocket.send_text = AsyncMock()
        mock_websocket.close = AsyncMock()

        with patch('src.modules.calls.api.calls_router.authenticate_by_token', return_value=None):
            from src.modules.calls.api.calls_router import call
            await call(mock_websocket)

            mock_websocket.send_text.assert_called_with(json.dumps({"error": "Invalid token"}))

    @pytest.mark.asyncio
    async def test_call_websocket_success(self):
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(return_value=json.dumps({"auth": "valid_token"}))
        mock_websocket.send_text = AsyncMock()
        mock_websocket.close = AsyncMock()

        mock_user = MagicMock()
        mock_user.uuid = "test_uuid"

        mock_service = AsyncMock()
        mock_service.call = AsyncMock()

        with patch('src.modules.calls.api.calls_router.authenticate_by_token', return_value=mock_user):
            with patch('src.modules.calls.api.calls_router.get_calls_state_service', return_value=mock_service):
                from src.modules.calls.api.calls_router import call
                await call(mock_websocket)

                mock_service.call.assert_called_once()
