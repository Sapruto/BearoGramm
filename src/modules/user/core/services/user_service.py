from typing import Optional

from .verify_service import VerifyService, get_verify_service
from ..repositories.user_repository import UserRepository, get_user_repository
from ...models.entities.user_entity import UserEntity, UserFields
from ...models.dto.requests import SendCodeRequest, VerifyCodeRequest
from ...models.dto.responses import SendCodeResponse, VerifyCodeResponse

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

    async def get_login_token_and_register_if_not(
        self, request: SendCodeRequest
    ) -> SendCodeResponse:
        try:
            phone_number = request.phone_number.strip()

            user = await self.user_repository.get_by_field(
                value=phone_number, field=UserFields.PHONE_NUMBER
            )

            if not user:
                new_user = UserEntity(phone_number=phone_number)
                user = await self.user_repository.save(new_user)

                if not isinstance(user, UserEntity):
                    return SendCodeResponse(
                        success=False, error_message="Failed to create user"
                    )

            code = await self.verify_service.send_login_code(
                user_uuid=str(user.uuid), phone_number=phone_number
            )

            if not code:
                return SendCodeResponse(
                    success=False, error_message="Failed to send code"
                )

            return SendCodeResponse(success=True)

        except Exception as e:
            logger.error(f"Error in get_login_token: {e}")
            return SendCodeResponse(
                success=False, error_message="Failed to get login token"
            )

    async def verify_phone(self, request: VerifyCodeRequest) -> VerifyCodeResponse:
        try:
            phone_number = request.phone_number.strip()
            code = request.code.strip()

            is_valid = await self.verify_service.verify_code(code)

            if not is_valid:
                return VerifyCodeResponse(
                    success=False, error_message="Invalid or expired code"
                )

            user = await self.user_repository.get_by_field(
                value=phone_number, field=UserFields.PHONE_NUMBER
            )

            if not user:
                return VerifyCodeResponse(success=False, error_message="User not found")

            await self.verify_service.delete_code(code)

            session = await self.session_service.create_session(
                CreateSessionRequest(user_uuid=str(user.uuid))
            )

            return VerifyCodeResponse(
                success=True, token=session.token, user_uuid=str(user.uuid)
            )

        except Exception as e:
            logger.error(f"Error in verify_phone: {e}")
            return VerifyCodeResponse(
                success=False, error_message="Verification failed"
            )


def get_user_service() -> UserService:
    return UserService()
