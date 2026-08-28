import pytest

from src.modules.messages.core.repositories.mappers.websocket_state_mapper import WebSocketStateMapper
from src.modules.messages.models.entities.websocket_state_entity import WebSocketStateEntity, WebSocketStateFields


@pytest.mark.unit
class TestWebSocketStateMapper:
    def test_to_redis(self):
        mapper = WebSocketStateMapper()
        entity = WebSocketStateEntity(
            user_uuid="test_uuid",
            online=True,
            last_activity=True
        )

        redis_data = mapper.to_redis(entity)

        assert redis_data["user_uuid"] == "test_uuid"
        assert redis_data["online"] == "true"
        assert redis_data["last_activity"] == "true"

    def test_to_redis_offline(self):
        mapper = WebSocketStateMapper()
        entity = WebSocketStateEntity(
            user_uuid="test_uuid",
            online=False,
            last_activity=False
        )

        redis_data = mapper.to_redis(entity)

        assert redis_data["online"] == "false"
        assert redis_data["last_activity"] == "false"

    def test_to_entity(self):
        mapper = WebSocketStateMapper()
        redis_data = {
            "user_uuid": "test_uuid",
            "online": "true",
            "last_activity": "true"
        }

        entity = mapper.to_entity(redis_data)

        assert entity.user_uuid == "test_uuid"
        assert entity.online is True
        assert entity.last_activity is True

    def test_to_entity_with_strings(self):
        mapper = WebSocketStateMapper()
        redis_data = {
            "user_uuid": "test_uuid",
            "online": "true",
            "last_activity": "false"
        }

        entity = mapper.to_entity(redis_data)

        assert entity.online is True
        assert entity.last_activity is False

    def test_to_entity_missing_fields(self):
        mapper = WebSocketStateMapper()
        redis_data = {
            "user_uuid": "test_uuid"
        }

        entity = mapper.to_entity(redis_data)

        assert entity.user_uuid == "test_uuid"
        assert entity.online is False
        assert entity.last_activity is False

    def test_to_redis_value_bool(self):
        mapper = WebSocketStateMapper()

        field, value = mapper.to_redis_value(WebSocketStateFields.ONLINE, True)
        assert field == "online"
        assert value == "true"

        field, value = mapper.to_redis_value(WebSocketStateFields.ONLINE, False)
        assert field == "online"
        assert value == "false"

    def test_to_redis_value_string(self):
        mapper = WebSocketStateMapper()

        field, value = mapper.to_redis_value(WebSocketStateFields.USER_UUID, "test")
        assert field == "user_uuid"
        assert value == "test"

    def test_to_entity_value(self):
        mapper = WebSocketStateMapper()

        field, value = mapper.to_entity_value("online", "true")
        assert field == WebSocketStateFields.ONLINE
        assert value is True

        field, value = mapper.to_entity_value("online", "false")
        assert field == WebSocketStateFields.ONLINE
        assert value is False

    def test_to_redis_field(self):
        mapper = WebSocketStateMapper()
        assert mapper.to_redis_field(WebSocketStateFields.USER_UUID) == "user_uuid"
        assert mapper.to_redis_field(WebSocketStateFields.ONLINE) == "online"
        assert mapper.to_redis_field(WebSocketStateFields.LAST_ACTIVE) == "last_activity"

    def test_to_entity_field(self):
        mapper = WebSocketStateMapper()
        assert mapper.to_entity_field("user_uuid") == WebSocketStateFields.USER_UUID
        assert mapper.to_entity_field("online") == WebSocketStateFields.ONLINE
        assert mapper.to_entity_field("last_activity") == WebSocketStateFields.LAST_ACTIVE

    def test_key_prefix(self):
        mapper = WebSocketStateMapper()
        assert mapper.key_prefix == "ws:user"

    def test_storage_type(self):
        mapper = WebSocketStateMapper()
        assert mapper.storage_type == "hash"

    def test_field_mapping(self):
        mapper = WebSocketStateMapper()
        assert mapper.field_mapping[WebSocketStateFields.USER_UUID] == "user_uuid"
        assert mapper.field_mapping[WebSocketStateFields.ONLINE] == "online"
        assert mapper.field_mapping[WebSocketStateFields.LAST_ACTIVE] == "last_activity"
