import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.modules.sessions.models.entities.session_entity import (
    SessionEntity,
    SessionFields,
)
from src.modules.sessions.models.dto.session_dto import (
    SessionDTO,
    CreateSessionDTO,
    SessionResultDTO,
)
from src.modules.sessions.core.repositories.mappers.sessions_mapper import SessionMapper
from src.modules.sessions.core.repositories.sessions_repository import SessionRepository
from src.modules.sessions.core.services.session_service import SessionService
from src.modules.sessions.core.services.token_service import TokenService
from src.modules.sessions.api.session_service_api import SessionAPIService


@pytest.fixture
def sample_session_entity():
    return SessionEntity(
        user_uuid=str(uuid4()),
        token="test_token_123456",
        expired_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )


@pytest.fixture
def sample_session_dto():
    return SessionDTO(
        token="test_token_123456",
        user_uuid=str(uuid4()),
        expired_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )


@pytest.fixture
def mock_redis_client():
    client = MagicMock()
    client.hset = AsyncMock(return_value=1)
    client.hgetall = AsyncMock()
    client.hdel = AsyncMock(return_value=1)
    client.delete = AsyncMock(return_value=1)
    client.expire = AsyncMock(return_value=True)
    client.scan = AsyncMock(return_value=(0, []))
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.exists = AsyncMock(return_value=1)
    return client


@pytest.fixture
def session_mapper():
    return SessionMapper()


@pytest.fixture
def session_repository(mock_redis_client):
    repo = SessionRepository(redis_client=mock_redis_client)
    repo._index_enabled = False
    return repo


@pytest.fixture
def token_service():
    with patch(
        "src.modules.sessions.core.services.token_service.Settings"
    ) as mock_settings:
        mock_settings.JWT.SECRET_KEY = "test_secret_key_123456789"
        mock_settings.JWT.EXPIRE_MINUTES = 1440
        mock_settings.JWT.ALGORITHM = "HS256"
        return TokenService(secret_key="test_secret_key_123456789")


@pytest.fixture
def session_service(session_repository, token_service):
    service = SessionService(
        session_repository=session_repository,
        token_service=token_service,
        session_ttl_hours=24,
        max_sessions_per_user=5,
    )
    return service


@pytest.fixture
def session_api_service(session_service):
    return SessionAPIService(session_service=session_service)


@pytest.fixture
def mock_token_service():
    service = MagicMock(spec=TokenService)
    service.create_access_token = MagicMock(return_value="test_token_123456")
    service.verify_token = MagicMock(
        return_value={"user_uuid": str(uuid4()), "session_id": str(uuid4())}
    )
    service.decode_token = MagicMock(return_value={"user_uuid": str(uuid4())})
    return service
