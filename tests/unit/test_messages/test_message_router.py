import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import WebSocket

from src.modules.messages.api.message_router import message_router
from src.modules.messages.api.message_router_names import MessageRoutes, MessageRoutesURL


@pytest.mark.unit
class TestMessageRouter:
    def test_router_prefix(self):
        assert message_router.prefix == "/api/messages"

    def test_router_routes(self):
        routes = [route.path for route in message_router.routes]
        assert "/api/messages/send" in routes
        assert "/api/messages/update" in routes
        assert "/api/messages/delete" in routes
        assert "/api/messages/get" in routes

    def test_message_routes_enum(self):
        assert MessageRoutes.base == "/api/messages"
        assert MessageRoutes.send_message == "/send"
        assert MessageRoutes.update_message == "/update"
        assert MessageRoutes.delete_message == "/delete"
        assert MessageRoutes.get_messages == "/get"

    def test_message_routes_url(self):
        assert hasattr(MessageRoutesURL, 'send_message')
        assert hasattr(MessageRoutesURL, 'update_message')
        assert hasattr(MessageRoutesURL, 'delete_message')
        assert hasattr(MessageRoutesURL, 'get_messages')
