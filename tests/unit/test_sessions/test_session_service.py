import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.modules.sessions.core.services.session_service import SessionService
from src.modules.sessions.models.entities.session_entity import SessionEntity
from src.modules.sessions.models.dto.session_dto import CreateSessionDTO
from src.general.repository.redis.redis_query import RedisQuery


@pytest.mark.unit
class TestSessionService:
    @pytest.mark.asyncio
    async def test_create_session_success(self, session_service):
        user_uuid = str(uuid4())
        dto = CreateSessionDTO(user_uuid=user_uuid)

        session_service._session_repo.get_all = AsyncMock(return_value=[])
        session_service._session_repo.save = AsyncMock(return_value=MagicMock())

        result = await session_service.create_session(dto)

        assert result is not None
        assert result.user_uuid == user_uuid
        assert result.token is not None
        assert result.expires_in_seconds > 0

    @pytest.mark.asyncio
    async def test_create_session_with_max_sessions(self, session_service, session_repository):
        user_uuid = str(uuid4())

        existing_sessions = [
            SessionEntity(
                user_uuid=user_uuid,
                token=f"token_{i}",
                expired_at=datetime.now(timezone.utc) + timedelta(hours=1)
            )
            for i in range(5)
        ]

        session_repository.get_all = AsyncMock(return_value=existing_sessions)
        session_repository.delete = AsyncMock(return_value=1)
        session_repository.save = AsyncMock()

        dto = CreateSessionDTO(user_uuid=user_uuid)
        result = await session_service.create_session(dto)

        assert result is not None
        session_repository.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_session_exception(self, session_service, session_repository):
        session_repository.save = AsyncMock(side_effect=Exception("Redis error"))
        dto = CreateSessionDTO(user_uuid=str(uuid4()))

        with pytest.raises(Exception):
            await session_service.create_session(dto)

    @pytest.mark.asyncio
    async def test_validate_session_valid(self, session_service, session_repository, token_service):
        user_uuid = str(uuid4())
        token = "valid_token"

        session = SessionEntity(
            user_uuid=user_uuid,
            token=token,
            expired_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )

        session_repository.get = AsyncMock(return_value=session)
        token_service.verify_token = MagicMock(return_value={"user_uuid": user_uuid})

        result = await session_service.validate_session(token)

        assert result is not None
        assert result.user_uuid == user_uuid
        assert result.token == token

    @pytest.mark.asyncio
    async def test_validate_session_invalid_token(self, session_service, token_service):
        token_service.verify_token = MagicMock(return_value=None)

        result = await session_service.validate_session("invalid_token")

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_session_not_found(self, session_service, session_repository, token_service):
        token = "valid_token"
        token_service.verify_token = MagicMock(return_value={"user_uuid": str(uuid4())})
        session_repository.get = AsyncMock(return_value=None)

        result = await session_service.validate_session(token)

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_session_expired(self, session_service, session_repository, token_service):
        user_uuid = str(uuid4())
        token = "expired_token"

        session = SessionEntity(
            user_uuid=user_uuid,
            token=token,
            expired_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )

        session_repository.get = AsyncMock(return_value=session)
        session_repository.delete = AsyncMock(return_value=1)
        token_service.verify_token = MagicMock(return_value={"user_uuid": user_uuid})

        result = await session_service.validate_session(token)

        assert result is None
        session_repository.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_session_success(self, session_service):
        user_uuid = str(uuid4())
        old_token = "old_token"

        session_service.validate_session = AsyncMock(
            return_value=MagicMock(user_uuid=user_uuid, token=old_token)
        )
        session_service.create_session = AsyncMock(
            return_value=MagicMock(token="new_token", user_uuid=user_uuid)
        )
        session_service._session_repo.delete = AsyncMock(return_value=1)

        result = await session_service.refresh_session(old_token)

        assert result is not None
        assert result.token == "new_token"

    @pytest.mark.asyncio
    async def test_refresh_session_invalid(self, session_service):
        session_service.validate_session = AsyncMock(return_value=None)

        result = await session_service.refresh_session("invalid_token")

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_session_success(self, session_service, session_repository):
        session_repository.delete = AsyncMock(return_value=1)

        result = await session_service.delete_session("test_token")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_session_not_found(self, session_service, session_repository):
        session_repository.delete = AsyncMock(return_value=0)

        result = await session_service.delete_session("test_token")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_session_exception(self, session_service, session_repository):
        session_repository.delete = AsyncMock(side_effect=Exception("Redis error"))

        result = await session_service.delete_session("test_token")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_all_user_sessions(self, session_service, session_repository):
        user_uuid = str(uuid4())
        sessions = [
            SessionEntity(user_uuid=user_uuid, token=f"token_{i}", expired_at=datetime.now(timezone.utc))
            for i in range(3)
        ]

        session_repository.get_all = AsyncMock(return_value=sessions)
        session_repository.delete = AsyncMock(return_value=1)

        result = await session_service.delete_all_user_sessions(user_uuid)

        assert result == 3

    @pytest.mark.asyncio
    async def test_delete_all_user_sessions_empty(self, session_service, session_repository):
        session_repository.get_all = AsyncMock(return_value=[])

        result = await session_service.delete_all_user_sessions(str(uuid4()))

        assert result == 0

    @pytest.mark.asyncio
    async def test_get_user_sessions(self, session_service, session_repository):
        user_uuid = str(uuid4())
        sessions = [
            SessionEntity(user_uuid=user_uuid, token=f"token_{i}", expired_at=datetime.now(timezone.utc))
            for i in range(3)
        ]

        session_repository.get_all = AsyncMock(return_value=sessions)

        result = await session_service.get_user_sessions(user_uuid)

        assert len(result) == 3
        assert all(s.user_uuid == user_uuid for s in result)

    @pytest.mark.asyncio
    async def test_get_user_sessions_exception(self, session_service, session_repository):
        session_repository.get_all = AsyncMock(side_effect=Exception("Redis error"))

        result = await session_service.get_user_sessions(str(uuid4()))

        assert result == []

    @pytest.mark.asyncio
    async def test_get_session_by_token(self, session_service, session_repository):
        token = "test_token"
        session = SessionEntity(
            user_uuid=str(uuid4()),
            token=token,
            expired_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )

        session_repository.get = AsyncMock(return_value=session)

        result = await session_service.get_session_by_token(token)

        assert result is not None
        assert result.token == token

    @pytest.mark.asyncio
    async def test_get_session_by_token_not_found(self, session_service, session_repository):
        session_repository.get = AsyncMock(return_value=None)

        result = await session_service.get_session_by_token("invalid")

        assert result is None

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, session_service, session_repository):
        expired_sessions = [
            SessionEntity(
                user_uuid=str(uuid4()),
                token=f"token_{i}",
                expired_at=datetime.now(timezone.utc) - timedelta(hours=1)
            )
            for i in range(3)
        ]
        valid_sessions = [
            SessionEntity(
                user_uuid=str(uuid4()),
                token=f"token_{i}",
                expired_at=datetime.now(timezone.utc) + timedelta(hours=1)
            )
            for i in range(2)
        ]

        all_sessions = expired_sessions + valid_sessions
        session_repository.get_all = AsyncMock(return_value=all_sessions)
        session_repository.delete = AsyncMock(return_value=1)

        result = await session_service.cleanup_expired_sessions()

        assert result == 3

    @pytest.mark.asyncio
    async def test_is_token_valid(self, session_service):
        session_service.validate_session = AsyncMock(return_value=MagicMock())

        result = await session_service.is_token_valid("valid_token")

        assert result is True

    @pytest.mark.asyncio
    async def test_is_token_valid_invalid(self, session_service):
        session_service.validate_session = AsyncMock(return_value=None)

        result = await session_service.is_token_valid("invalid_token")

        assert result is False

    @pytest.mark.asyncio
    async def test_get_active_sessions_count(self, session_service, session_repository):
        user_uuid = str(uuid4())
        sessions = [
            SessionEntity(user_uuid=user_uuid, token="token_1",
                          expired_at=datetime.now(timezone.utc) + timedelta(hours=1)),
            SessionEntity(user_uuid=user_uuid, token="token_2",
                          expired_at=datetime.now(timezone.utc) + timedelta(hours=2)),
            SessionEntity(user_uuid=user_uuid, token="token_3",
                          expired_at=datetime.now(timezone.utc) - timedelta(hours=1)),
        ]

        session_repository.get_all = AsyncMock(return_value=sessions)

        result = await session_service.get_active_sessions_count(user_uuid)

        assert result == 2

    @pytest.mark.asyncio
    async def test_get_active_sessions_count_exception(self, session_service, session_repository):
        session_repository.get_all = AsyncMock(side_effect=Exception("Redis error"))

        result = await session_service.get_active_sessions_count(str(uuid4()))

        assert result == 0
