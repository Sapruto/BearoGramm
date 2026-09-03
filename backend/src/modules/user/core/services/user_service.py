from typing import Optional

from .verify_service import VerifyService, get_verify_service
from ..repositories.user_repository import UserRepository, get_user_repository
from ..exceptions import (
    FailedToCreateUser,
    FailedToSendCode,
    FailedToGetLoginToken,
    InvalidOrExpiredCode,
    UserNotFound,
    VerificationFailed,
    SessionCreationFailed,
    InvalidPhoneNumber,
)
from ...models.entities.user_entity import UserEntity, UserFields
from ...models.dto.requests import SendCodeRequest, VerifyCodeRequest
from ...models.dto.responses import SendCodeResponse, VerifyCodeResponse

from src.general.repository.sql.sql_query import SqlQuery
from src.core.logger import get_logger
from src.modules.sessions import (
    SessionAPIService,
    get_session_service_api,
    CreateSessionRequest,
)

logger = get_logger(__name__)


class UserService:
    def __init__(
        self,
        user_repository: Optional[UserRepository] = None,
        verify_service: Optional[VerifyService] = None,
        session_service: Optional[SessionAPIService] = None,
    ):
        self.user_repository = user_repository or get_user_repository()
        self.verify_service = verify_service or get_verify_service()
        self.session_service = session_service or get_session_service_api()

    async def send_code_and_register_if_not(
        self, request: SendCodeRequest
    ) -> SendCodeResponse:
        try:
            phone_number = request.phone_number.strip()
            if not phone_number:
                raise InvalidPhoneNumber(phone_number)

            user = await self.user_repository.get_by_field(
                value=phone_number, field=UserFields.PHONE_NUMBER
            )

            if not user:
                new_user = UserEntity(phone_number=phone_number)
                user = await self.user_repository.save(new_user)

                if not user:
                    raise FailedToCreateUser(phone_number, "Repository returned None")

            code = await self.verify_service.send_login_code(
                user_uuid=str(user.uuid), phone_number=phone_number
            )

            if not code:
                raise FailedToSendCode(phone_number, str(user.uuid), "Verify service returned None")

            return SendCodeResponse()

        except (InvalidPhoneNumber, FailedToCreateUser, FailedToSendCode):
            raise

        except Exception as e:
            logger.error(f"Error in send_code_and_register_if_not: {e}")
            raise FailedToGetLoginToken(request.phone_number, str(e))

    async def verify_phone(self, request: VerifyCodeRequest) -> VerifyCodeResponse:
        try:
            phone_number = request.phone_number.strip()
            code = request.code.strip()

            if not phone_number:
                raise InvalidPhoneNumber(phone_number)
            if not code:
                raise InvalidOrExpiredCode(phone_number)

            is_valid = await self.verify_service.verify_code(code)

            if not is_valid:
                raise InvalidOrExpiredCode(phone_number)

            user = await self.user_repository.get(
                SqlQuery[UserFields]().add_filter(field=UserFields.PHONE_NUMBER, value=phone_number)
            )

            if not user:
                raise UserNotFound(phone_number)

            await self.verify_service.delete_code(code)

            session = await self.session_service.create_session(
                CreateSessionRequest(user_uuid=str(user.uuid))
            )
            if not session:
                raise SessionCreationFailed(str(user.uuid), "Session service returned None")

            return VerifyCodeResponse(token=session.token, user_uuid=str(user.uuid), user=user)

        except (InvalidPhoneNumber,
            InvalidOrExpiredCode,
            UserNotFound,
            SessionCreationFailed,
        ):
            raise

        except Exception as e:
            logger.error(f"Error in verify_phone: {e}")
            raise VerificationFailed(request.phone_number, str(e))


def get_user_service() -> UserService:
    return UserService()
