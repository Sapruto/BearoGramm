from typing import Optional, List
from datetime import datetime, timedelta, timezone
import uuid

from src.core.logger import get_logger
from src.general.repository.redis.redis_query import RedisQuery

from .token_service import TokenService, get_token_service
from ..repositories.sessions_repository import SessionRepository, get_session_repository
from ...models.entities.session_entity import SessionEntity, SessionFields
from ...models.dto.session_dto import SessionDTO, CreateSessionDTO, SessionResultDTO

logger = get_logger(__name__)

class SessionService:
    def __init__(self, session_repository: Optional[SessionRepository] = None, token_service: Optional[TokenService] = None, session_ttl_hours: int = 24, max_sessions_per_user: Optional[int] = None):
        self._session_repo = session_repository or get_session_repository()
        self._token_service = token_service or get_token_service()
        self._ttl_hours = session_ttl_hours
        self._max_sessions = max_sessions_per_user

    async def create_session(self, dto: CreateSessionDTO) -> SessionResultDTO:
        try:
            if self._max_sessions:
                query = RedisQuery[SessionFields]().add_filter(SessionFields.USER_UUID, dto.user_uuid)
                sessions = await self._session_repo.get_all(query)

                if len(sessions) >= self._max_sessions:
                    sessions.sort(key=lambda s: s.expired_at or datetime.min)
                    delete_query = RedisQuery[SessionFields]().add_filter(SessionFields.TOKEN, sessions[0].token)
                    await self._session_repo.delete(delete_query)

            session_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)

            token_data = {
                "user_uuid": dto.user_uuid,
                "session_id": session_id,
                "created_at": now.isoformat()
            }

            token = self._token_service.create_access_token(
                token_data,
                expires_delta=timedelta(hours=self._ttl_hours)
            )

            expires_at = now + timedelta(hours=self._ttl_hours)
            session = SessionEntity(
                user_uuid=dto.user_uuid,
                token=token,
                expired_at=expires_at
            )

            await self._session_repo.save(session)

            logger.info(f"Session created for user {dto.user_uuid}")

            return SessionResultDTO(
                token=token,
                user_uuid=dto.user_uuid,
                expires_at=expires_at,
                expires_in_seconds=self._ttl_hours * 3600
            )

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    async def validate_session(self, token: str) -> Optional[SessionDTO]:
        try:
            payload = self._token_service.verify_token(token)
            if not payload:
                logger.warning("Invalid or expired token")
                return None

            query = RedisQuery[SessionFields]().add_filter(SessionFields.TOKEN, token)
            session = await self._session_repo.get(query)

            if not session:
                logger.warning(f"Session not found for token")
                return None

            now = datetime.now(timezone.utc)
            if session.expired_at and session.expired_at < now:
                delete_query = RedisQuery[SessionFields]().add_filter(SessionFields.TOKEN, token)
                await self._session_repo.delete(delete_query)
                logger.warning(f"Session expired for token")
                return None

            return SessionDTO(
                token=session.token,
                user_uuid=session.user_uuid,
                expired_at=session.expired_at
            )

        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None

    async def refresh_session(self, token: str) -> Optional[SessionResultDTO]:
        try:
            old_session = await self.validate_session(token)
            if not old_session:
                logger.warning(f"Failed to refresh session: invalid token")
                return None

            create_dto = CreateSessionDTO(user_uuid=old_session.user_uuid)
            new_session = await self.create_session(create_dto)

            delete_query = RedisQuery[SessionFields]().add_filter(SessionFields.TOKEN, token)
            await self._session_repo.delete(delete_query)

            logger.info(f"Session refreshed for user {old_session.user_uuid}")
            return new_session

        except Exception as e:
            logger.error(f"Error refreshing session: {e}")
            return None

    async def delete_session(self, token: str) -> bool:
        try:
            query = RedisQuery[SessionFields]().add_filter(SessionFields.TOKEN, token)
            deleted = await self._session_repo.delete(query)

            if deleted > 0:
                logger.info(f"Session deleted: {token[:10]}...")
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False

    async def delete_all_user_sessions(self, user_uuid: str) -> int:
        try:
            query = RedisQuery[SessionFields]().add_filter(SessionFields.USER_UUID, user_uuid)
            sessions = await self._session_repo.get_all(query)

            deleted = 0
            for session in sessions:
                delete_query = RedisQuery[SessionFields]().add_filter(SessionFields.TOKEN, session.token)
                if await self._session_repo.delete(delete_query) > 0:
                    deleted += 1

            logger.info(f"Deleted {deleted} sessions for user {user_uuid}")
            return deleted

        except Exception as e:
            logger.error(f"Error deleting user sessions: {e}")
            return 0

    async def get_user_sessions(self, user_uuid: str) -> List[SessionDTO]:
        try:
            query = RedisQuery[SessionFields]().add_filter(SessionFields.USER_UUID, user_uuid)
            sessions = await self._session_repo.get_all(query)

            return [
                SessionDTO(
                    token=s.token,
                    user_uuid=s.user_uuid,
                    expired_at=s.expired_at
                )
                for s in sessions
            ]
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []

    async def get_session_by_token(self, token: str) -> Optional[SessionDTO]:
        try:
            query = RedisQuery[SessionFields]().add_filter(SessionFields.TOKEN, token)
            session = await self._session_repo.get(query)

            if not session:
                return None

            return SessionDTO(
                token=session.token,
                user_uuid=session.user_uuid,
                expired_at=session.expired_at
            )
        except Exception as e:
            logger.error(f"Error getting session by token: {e}")
            return None

    async def cleanup_expired_sessions(self, batch_size: int = 100) -> int:
        try:
            now = datetime.now(timezone.utc)
            query = RedisQuery[SessionFields]()
            all_sessions = await self._session_repo.get_all(query)

            deleted = 0
            for session in all_sessions:
                if session.expired_at and session.expired_at < now:
                    delete_query = RedisQuery[SessionFields]().add_filter(SessionFields.TOKEN, session.token)
                    if await self._session_repo.delete(delete_query) > 0:
                        deleted += 1

                    if deleted % batch_size == 0:
                        logger.info(f"Cleaned up {deleted} expired sessions")

            logger.info(f"Total cleaned up {deleted} expired sessions")
            return deleted

        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
            return 0

    async def is_token_valid(self, token: str) -> bool:
        try:
            result = await self.validate_session(token)
            return result is not None
        except Exception as e:
            logger.error(f"Error checking token validity: {e}")
            return False

    async def get_active_sessions_count(self, user_uuid: str) -> int:
        try:
            query = RedisQuery[SessionFields]().add_filter(SessionFields.USER_UUID, user_uuid)
            sessions = await self._session_repo.get_all(query)

            now = datetime.now(timezone.utc)
            return sum(1 for s in sessions if s.expired_at and s.expired_at > now)

        except Exception as e:
            logger.error(f"Error counting active sessions: {e}")
            return 0

def get_session_service() -> SessionService:
    return SessionService()
