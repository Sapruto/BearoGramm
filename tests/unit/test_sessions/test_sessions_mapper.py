import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.modules.sessions.core.repositories.mappers.sessions_mapper import SessionMapper
from src.modules.sessions.models.entities.session_entity import SessionEntity, SessionFields


@pytest.mark.unit
class TestSessionMapper:
    def test_to_redis(self, session_mapper, sample_session_entity):
        redis_data = session_mapper.to_redis(sample_session_entity)

        assert redis_data["user_uuid"] == sample_session_entity.user_uuid
        assert redis_data["token"] == sample_session_entity.token
        assert redis_data["expired_at"] == sample_session_entity.expired_at.isoformat()

    def test_to_entity(self, session_mapper):
        user_uuid = str(uuid4())
        token = "test_token"
        expired_at = datetime.now(timezone.utc) + timedelta(hours=24)

        redis_data = {
            "user_uuid": user_uuid,
            "token": token,
            "expired_at": expired_at.isoformat()
        }

        entity = session_mapper.to_entity(redis_data)

        assert entity.user_uuid == user_uuid
        assert entity.token == token
        assert entity.expired_at == expired_at

    def test_to_entity_without_expired_at(self, session_mapper):
        user_uuid = str(uuid4())
        token = "test_token"

        redis_data = {
            "user_uuid": user_uuid,
            "token": token
        }

        entity = session_mapper.to_entity(redis_data)

        assert entity.user_uuid == user_uuid
        assert entity.token == token
        assert entity.expired_at is None

    def test_to_redis_value(self, session_mapper):
        field, value = session_mapper.to_redis_value(
            SessionFields.USER_UUID,
            "test_uuid"
        )
        assert field == "user_uuid"
        assert value == "test_uuid"

        field, value = session_mapper.to_redis_value(
            SessionFields.TOKEN,
            "test_token"
        )
        assert field == "token"
        assert value == "test_token"

    def test_to_redis_value_expired_at(self, session_mapper):
        now = datetime.now(timezone.utc)
        field, value = session_mapper.to_redis_value(
            SessionFields.EXPIRED_AT,
            now
        )
        assert field == "expired_at"
        assert value == now.isoformat()

    def test_to_entity_value(self, session_mapper):
        field, value = session_mapper.to_entity_value(
            "user_uuid",
            "test_uuid"
        )
        assert field == SessionFields.USER_UUID
        assert value == "test_uuid"

        field, value = session_mapper.to_entity_value(
            "token",
            "test_token"
        )
        assert field == SessionFields.TOKEN
        assert value == "test_token"

    def test_to_entity_value_expired_at(self, session_mapper):
        now = datetime.now(timezone.utc)
        field, value = session_mapper.to_entity_value(
            "expired_at",
            now.isoformat()
        )
        assert field == SessionFields.EXPIRED_AT
        assert value == now

    def test_get_id_field(self, session_mapper):
        assert session_mapper.get_id_field() == SessionFields.TOKEN

    def test_get_id_from_entity(self, session_mapper, sample_session_entity):
        assert session_mapper.get_id_from_entity(sample_session_entity) == sample_session_entity.token

    def test_field_mapping(self, session_mapper):
        assert session_mapper.field_mapping[SessionFields.USER_UUID] == "user_uuid"
        assert session_mapper.field_mapping[SessionFields.TOKEN] == "token"
        assert session_mapper.field_mapping[SessionFields.EXPIRED_AT] == "expired_at"

    def test_key_prefix(self, session_mapper):
        assert session_mapper.key_prefix == "session"

    def test_storage_type(self, session_mapper):
        assert session_mapper.storage_type == "hash"
