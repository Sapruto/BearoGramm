from typing import Optional

from src.general.repository.sql.sql_query import SqlQuery
from src.modules.sessions import SessionAPIService, get_session_service_api
from src.core.logger import get_logger

from .models import UserAPIModel, UserSessionsAPIModel, UserSessionResponseAPIModel
from ...core.repositories.user_repository import UserRepository, get_user_repository
from ...models.entities.user_entity import UserFields

logger = get_logger(__name__)


class UserServiceAPI:
    def __init__(
        self,
        user_repository: Optional[UserRepository] = None,
        session_service: Optional[SessionAPIService] = None,
    ):
        self.user_repository = user_repository or get_user_repository()
        self.session_service = session_service or get_session_service_api()

    @staticmethod
    def _to_user_api(user) -> UserAPIModel:
        return UserAPIModel(
            uuid=user.uuid,
            phone_number=user.phone_number,
            email=user.email,
            username=user.username,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def update(self, user_uuid: str, email: Optional[str] = None, username: Optional[str] = None) -> bool:
        query = SqlQuery[UserFields]().add_filter(field=UserFields.UUID, value=user_uuid)
        user = await self.user_repository.get(query)

        if not user:
            return False
        if email:
            user.email = email
        if username:
            user.username = username
        result = await self.user_repository.save(user, to_update=True)
        return result

    async def get_user_by_uuid(self, user_uuid: str) -> Optional[UserAPIModel]:
        try:
            query = SqlQuery[UserFields]().add_filter(field=UserFields.UUID, value=user_uuid)
            user = await self.user_repository.get(query)

            if not user:
                return None

            return UserServiceAPI._to_user_api(user)

        except Exception as e:
            logger.error(f"Error getting user by UUID: {e}")
            return None

    async def get_user_by_phone(self, phone_number: str) -> Optional[UserAPIModel]:
        try:
            query = SqlQuery[UserFields]().add_filter(field=UserFields.PHONE_NUMBER, value=phone_number)
            user = await self.user_repository.get(query)

            if not user:
                return None

            return UserServiceAPI._to_user_api(user)

        except Exception as e:
            logger.error(f"Error getting user by phone: {e}")
            return None

    async def get_user_sessions(self, user_uuid: str) -> UserSessionResponseAPIModel:
        try:
            sessions_response = await self.session_service.get_user_sessions(user_uuid)

            sessions = [
                UserSessionsAPIModel(
                    token=s.token, user_uuid=s.user_uuid, expires_at=s.expired_at
                )
                for s in sessions_response.sessions
            ]

            return UserSessionResponseAPIModel(
                user_uuid=user_uuid, sessions=sessions, total=sessions_response.total
            )

        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return UserSessionResponseAPIModel(
                user_uuid=user_uuid, sessions=[], total=0
            )

    async def get_user_by_username(self, username: str):
        try:
            query = SqlQuery[UserFields]().add_filter(field=UserFields.USERNAME, value=username)
            user = await self.user_repository.get(query)

            if not user:
                return None

            return UserServiceAPI._to_user_api(user)

        except Exception as e:
            logger.error(f"Error getting user by phone: {e}")
            return None

    async def get_user_by_email(self, email: str):
        try:
            query = SqlQuery[UserFields]().add_filter(field=UserFields.EMAIL, value=email)
            user = await self.user_repository.get(query)

            if not user:
                return None

            return UserServiceAPI._to_user_api(user)

        except Exception as e:
            logger.error(f"Error getting user by phone: {e}")
            return None

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
