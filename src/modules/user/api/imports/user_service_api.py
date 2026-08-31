from typing import Optional

from src.modules.sessions import SessionAPIService, get_session_service_api
from src.core.logger import get_logger

from .models import UserAPIModel, UserSessionsAPIModel, UserSessionResponseAPIModel
from ...core.repositories.user_repository import UserRepository, get_user_repository
from ...models.entities.user_entity import UserFields

logger = get_logger(__name__)

class UserServiceAPI:
    def __init__(self, user_repository: Optional[UserRepository] = None, session_service: Optional[SessionAPIService] = None):
        self.user_repository = user_repository or get_user_repository()
        self.session_service = session_service or get_session_service_api()

    async def get_user_by_uuid(self, user_uuid: str) -> Optional[UserAPIModel]:
        try:
            user = await self.user_repository.get_by_field(
                value=user_uuid,
                field=UserFields.UUID
            )

            if not user:
                return None

            return UserAPIModel(
                uuid=user.uuid,
                phone_number=user.phone_number,
                created_at=user.created_at,
                updated_at=user.updated_at
            )

        except Exception as e:
            logger.error(f"Error getting user by UUID: {e}")
            return None

    async def get_user_by_phone(self, phone_number: str) -> Optional[UserAPIModel]:
        try:
            user = await self.user_repository.get_by_field(
                value=phone_number,
                field=UserFields.PHONE_NUMBER
            )

            if not user:
                return None

            return UserAPIModel(
                uuid=user.uuid,
                phone_number=user.phone_number,
                created_at=user.created_at,
                updated_at=user.updated_at
            )

        except Exception as e:
            logger.error(f"Error getting user by phone: {e}")
            return None

    async def get_user_sessions(self, user_uuid: str) -> UserSessionResponseAPIModel:
        try:
            sessions_response = await self.session_service.get_user_sessions(user_uuid)

            sessions = [
                UserSessionsAPIModel(
                    token=s.token,
                    user_uuid=s.user_uuid,
                    expires_at=s.expired_at
                )
                for s in sessions_response.sessions
            ]

            return UserSessionResponseAPIModel(
                user_uuid=user_uuid,
                sessions=sessions,
                total=sessions_response.total
            )

        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return UserSessionResponseAPIModel(
                user_uuid=user_uuid,
                sessions=[],
                total=0
            )

    async def delete_user_session(self, token: str) -> bool:
        try:
            return await self.session_service.delete_session(token)
        except Exception as e:
            logger.error(f"Error deleting user session: {e}")
            return False

    async def delete_all_user_sessions(self, user_uuid: str) -> int:
        try:
            return await self.session_service.delete_all_user_sessions(user_uuid)
        except Exception as e:
            logger.error(f"Error deleting all user sessions: {e}")
            return 0

def get_user_service_api() -> UserServiceAPI:
    return UserServiceAPI()
