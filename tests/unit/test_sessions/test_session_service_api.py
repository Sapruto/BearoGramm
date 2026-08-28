import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.modules.sessions.api.session_service_api import SessionAPIService
from src.modules.sessions.api.models import (
    CreateSessionRequest,
    CreateSessionResponse,
    ValidateSessionResponse,
    RefreshSessionResponse,
    DeleteSessionResponse,
    UserSessionsResponse
)
from src.modules.sessions.models.dto.session_dto import SessionResultDTO, SessionDTO


@pytest.mark.unit
class TestSessionAPIService:
    @pytest.mark.asyncio
    async def test_create_session(self, session_api_service, session_service):
        user_uuid = str(uuid4())
        request = CreateSessionRequest(user_uuid=user_uuid)

        result_dto = SessionResultDTO(
            token="test_token",
            user_uuid=user_uuid,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            expires_in_seconds=86400
        )
        session_service.create_session = AsyncMock(return_value=result_dto)

        response = await session_api_service.create_session(request)

        assert isinstance(response, CreateSessionResponse)
        assert response.token == "test_token"
        assert response.user_uuid == user_uuid
        assert response.expires_in_seconds == 86400

    @pytest.mark.asyncio
    async def test_validate_session_valid(self, session_api_service, session_service):
        token = "valid_token"
        user_uuid = str(uuid4())

        session_dto = SessionDTO(
            token=token,
            user_uuid=user_uuid,
            expired_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        session_service.validate_session = AsyncMock(return_value=session_dto)

        response = await session_api_service.validate_session(token)

        assert isinstance(response, ValidateSessionResponse)
        assert response.is_valid is True
        assert response.user_uuid == user_uuid

    @pytest.mark.asyncio
    async def test_validate_session_invalid(self, session_api_service, session_service):
        session_service.validate_session = AsyncMock(return_value=None)

        response = await session_api_service.validate_session("invalid_token")

        assert isinstance(response, ValidateSessionResponse)
        assert response.is_valid is False
        assert response.user_uuid is None

    @pytest.mark.asyncio
    async def test_refresh_session_success(self, session_api_service, session_service):
        user_uuid = str(uuid4())
        old_token = "old_token"

        result_dto = SessionResultDTO(
            token="new_token",
            user_uuid=user_uuid,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            expires_in_seconds=86400
        )
        session_service.refresh_session = AsyncMock(return_value=result_dto)

        response = await session_api_service.refresh_session(old_token)

        assert isinstance(response, RefreshSessionResponse)
        assert response.token == "new_token"
        assert response.user_uuid == user_uuid

    @pytest.mark.asyncio
    async def test_refresh_session_failed(self, session_api_service, session_service):
        session_service.refresh_session = AsyncMock(return_value=None)

        with pytest.raises(ValueError):
            await session_api_service.refresh_session("invalid_token")

    @pytest.mark.asyncio
    async def test_delete_session_success(self, session_api_service, session_service):
        session_service.delete_session = AsyncMock(return_value=True)

        response = await session_api_service.delete_session("test_token")

        assert isinstance(response, DeleteSessionResponse)
        assert response.success is True

    @pytest.mark.asyncio
    async def test_delete_session_failed(self, session_api_service, session_service):
        session_service.delete_session = AsyncMock(return_value=False)

        response = await session_api_service.delete_session("test_token")

        assert isinstance(response, DeleteSessionResponse)
        assert response.success is False

    @pytest.mark.asyncio
    async def test_get_user_sessions(self, session_api_service, session_service):
        user_uuid = str(uuid4())
        sessions = [
            SessionDTO(token="token_1", user_uuid=user_uuid, expired_at=datetime.now(timezone.utc)),
            SessionDTO(token="token_2", user_uuid=user_uuid, expired_at=datetime.now(timezone.utc)),
        ]
        session_service.get_user_sessions = AsyncMock(return_value=sessions)

        response = await session_api_service.get_user_sessions(user_uuid)

        assert isinstance(response, UserSessionsResponse)
        assert response.user_uuid == user_uuid
        assert response.total == 2
        assert len(response.sessions) == 2

    @pytest.mark.asyncio
    async def test_delete_all_user_sessions(self, session_api_service, session_service):
        user_uuid = str(uuid4())
        session_service.delete_all_user_sessions = AsyncMock(return_value=3)

        result = await session_api_service.delete_all_user_sessions(user_uuid)

        assert result == 3

    @pytest.mark.asyncio
    async def test_get_session_service_api(self):
        from src.modules.sessions.api.session_service_api import get_session_service_api
        service = get_session_service_api()
        assert isinstance(service, SessionAPIService)
