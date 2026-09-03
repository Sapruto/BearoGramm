import pytest

from src.modules.messages.models.entities.websocket_state_entity import (
    WebSocketStateEntity,
    WebSocketStateFields,
)


@pytest.mark.unit
class TestWebSocketStateEntity:
    def test_websocket_state_entity_creation(self):
        entity = WebSocketStateEntity(
            user_uuid="test_uuid", online=True, last_activity=True
        )

        assert entity.user_uuid == "test_uuid"
        assert entity.online is True
        assert entity.last_activity is True

    def test_websocket_state_entity_offline(self):
        entity = WebSocketStateEntity(
            user_uuid="test_uuid", online=False, last_activity=False
        )

        assert entity.online is False
        assert entity.last_activity is False

    def test_websocket_state_fields_enum(self):
        assert WebSocketStateFields.USER_UUID.value == "user_uuid"
        assert WebSocketStateFields.ONLINE.value == "online"
        assert WebSocketStateFields.LAST_ACTIVE.value == "last_active"

    def test_websocket_state_fields_str(self):
        field = WebSocketStateFields.ONLINE
        assert str(field) == "online"
