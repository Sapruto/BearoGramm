import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.modules.sessions.models.dto.session_dto import (
    SessionDTO,
    CreateSessionDTO,
    SessionResultDTO,
)


@pytest.mark.unit
class TestSessionDTO:
    def test_session_dto_creation(self):
        dto = SessionDTO(
            token="test_token",
            user_uuid=str(uuid4()),
            expired_at=datetime.now(timezone.utc),
        )
        assert dto.token == "test_token"
        assert dto.user_uuid is not None
        assert dto.expired_at is not None

    def test_create_session_dto(self):
        user_uuid = str(uuid4())
        dto = CreateSessionDTO(user_uuid=user_uuid)
        assert dto.user_uuid == user_uuid

    def test_session_result_dto(self):
        now = datetime.now(timezone.utc)
        dto = SessionResultDTO(
            token="test_token",
            user_uuid=str(uuid4()),
            expires_at=now,
            expires_in_seconds=3600,
        )
        assert dto.token == "test_token"
        assert dto.expires_in_seconds == 3600
