import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.modules.sessions.models.entities.session_entity import (
    SessionEntity,
    SessionFields,
)


@pytest.mark.unit
class TestSessionEntity:
    def test_session_entity_creation(self):
        user_uuid = str(uuid4())
        token = "test_token"
        expired_at = datetime.now(timezone.utc) + timedelta(hours=24)

        session = SessionEntity(user_uuid=user_uuid, token=token, expired_at=expired_at)

        assert session.user_uuid == user_uuid
        assert session.token == token
        assert session.expired_at == expired_at

    def test_session_entity_optional_fields(self):
        session = SessionEntity(user_uuid=str(uuid4()), token=None, expired_at=None)

        assert session.token is None
        assert session.expired_at is None

    def test_session_fields_enum(self):
        assert SessionFields.USER_UUID == "user_uuid"
        assert SessionFields.TOKEN == "token"
        assert SessionFields.EXPIRED_AT == "expired_at"

    def test_session_fields_str(self):
        field = SessionFields.TOKEN
        assert str(field) == "token"
