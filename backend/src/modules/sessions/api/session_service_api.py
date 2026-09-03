from typing import Optional

from .models import (
    CreateSessionRequest,
    CreateSessionResponse,
    ValidateSessionResponse,
    RefreshSessionResponse,
    DeleteSessionResponse,
    SessionInfoResponse,
    UserSessionsResponse,
)
from ..core.services.session_service import SessionService, get_session_service
from ..models.dto.session_dto import CreateSessionDTO


class SessionAPIService:
    def __init__(self, session_service: Optional[SessionService] = None):
        self._session_service = session_service or get_session_service()

    async def create_session(
        self, request: CreateSessionRequest
    ) -> CreateSessionResponse:
        dto = CreateSessionDTO(user_uuid=request.user_uuid)
        result = await self._session_service.create_session(dto)

        return CreateSessionResponse(
            token=result.token,
            user_uuid=result.user_uuid,
            expires_at=result.expires_at,
            expires_in_seconds=result.expires_in_seconds,
        )

    async def validate_session(self, token: str) -> ValidateSessionResponse:
        session = await self._session_service.validate_session(token)

        if session:
            return ValidateSessionResponse(
                is_valid=True,
                user_uuid=session.user_uuid,
                expired_at=session.expired_at,
            )
        return ValidateSessionResponse(is_valid=False)

    async def refresh_session(self, token: str) -> RefreshSessionResponse:
        result = await self._session_service.refresh_session(token)

        if not result:
            raise ValueError("Failed to refresh session")

        return RefreshSessionResponse(
            token=result.token,
            user_uuid=result.user_uuid,
            expires_at=result.expires_at,
            expires_in_seconds=result.expires_in_seconds,
        )

    async def delete_session(self, token: str) -> DeleteSessionResponse:
        success = await self._session_service.delete_session(token)
        return DeleteSessionResponse(success=success)

    async def get_user_sessions(self, user_uuid: str) -> UserSessionsResponse:
        sessions = await self._session_service.get_user_sessions(user_uuid)

        session_infos = [
            SessionInfoResponse(
                token=s.token, user_uuid=s.user_uuid, expired_at=s.expired_at
            )
            for s in sessions
        ]

        return UserSessionsResponse(
            user_uuid=user_uuid, sessions=session_infos, total=len(session_infos)
        )

    async def delete_all_user_sessions(self, user_uuid: str) -> int:
        return await self._session_service.delete_all_user_sessions(user_uuid)


def get_session_service_api() -> SessionAPIService:
    return SessionAPIService()
