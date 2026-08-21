from typing import Optional
from enum import Enum

from src.core.logger import get_logger
from src.modules.sessions import SessionAPIService, get_session_service_api, CreateSessionRequest

from ..client.client_sms_api import ClientSMS, get_client_sms_api

logger = get_logger(__name__)

class VerifyType(str, Enum):
    PHONE_VERIFY = "phone_verify"
    LOGIN = "login"

class VerifyService:
    def __init__(self, session_service: Optional[SessionAPIService] = None, sms_api: Optional[ClientSMS] = None):
        self.session_service = session_service or get_session_service_api()
        self.sms_api = sms_api or get_client_sms_api()

    async def send_phone_verify_code(self, user_uuid: str, phone_number: str) -> Optional[str]:
        try:
            session = await self.session_service.create_session(request=CreateSessionRequest(user_uuid=user_uuid))

            code = session.token
            expires_in = session.expires_in_seconds // 60

            sent = await self.sms_api.send_verify_code(
                phone_number=phone_number,
                code=code,
                time_of_live_per_minuts=expires_in
            )

            if not sent:
                await self.session_service.delete_session(code)
                return None

            return code

        except Exception as e:
            logger.error(f"Error sending phone verify code: {e}")
            return None

    async def send_login_code(self, user_uuid: str, phone_number: str) -> Optional[str]:
        try:
            session = await self.session_service.create_session(request=CreateSessionRequest(user_uuid=user_uuid))

            code = session.token
            expires_in = session.expires_in_seconds // 60

            sent = await self.sms_api.send_login_code(
                phone_number=phone_number,
                code=code,
                time_of_live_per_minuts=expires_in
            )

            if not sent:
                await self.session_service.delete_session(code)
                return None

            return code

        except Exception as e:
            logger.error(f"Error sending login code: {e}")
            return None

    async def verify_code(self, code: str) -> bool:
        try:
            session = await self.session_service.validate_session(code)
            return session.is_valid
        except Exception as e:
            logger.error(f"Error verifying code: {e}")
            return False

    async def delete_code(self, code: str) -> bool:
        try:
            result = await self.session_service.delete_session(code)
            return result.success
        except Exception as e:
            logger.error(f"Error deleting code: {e}")
            return False

def get_verify_service() -> VerifyService:
    return VerifyService()
