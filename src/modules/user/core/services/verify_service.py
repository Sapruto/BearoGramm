from typing import Optional
from datetime import datetime, timedelta

from src.core.logger import get_logger
from src.general.repository.redis.redis_query import RedisQuery

from ..client.client_sms_api import ClientSMS, get_client_sms_api
from ..repositories.verification_code_repository import (
    VerificationCodeRepository,
    get_verification_code_repository,
    VerificationCodeEntity,
    VerificationCodeFields,
)

logger = get_logger(__name__)


class VerifyService:
    def __init__(
        self,
        verification_code_repository: Optional[VerificationCodeRepository] = None,
        sms_api: Optional[ClientSMS] = None,
    ):
        self.verification_code_repository = (
            verification_code_repository or get_verification_code_repository()
        )
        self.sms_api = sms_api or get_client_sms_api()

    async def send_phone_verify_code(
        self, user_uuid: str, phone_number: str
    ) -> Optional[str]:
        try:
            query = RedisQuery[VerificationCodeFields]().add_filter(
                VerificationCodeFields.PHONE, phone_number
            )
            await self.verification_code_repository.delete(query)

            code = self.verification_code_repository.gen_code()
            entity = VerificationCodeEntity(
                user_uuid=user_uuid,
                phone=phone_number,
                code=code,
                expired_at=datetime.now()
                + timedelta(seconds=self.verification_code_repository.ttl),
            )
            await self.verification_code_repository.save(entity)

            ttl_minutes = self.verification_code_repository.ttl // 60
            sent = await self.sms_api.send_verify_code(
                phone_number=phone_number,
                code=code,
                time_of_live_per_minuts=ttl_minutes,
            )

            if not sent:
                query = RedisQuery[VerificationCodeFields]().add_filter(
                    VerificationCodeFields.PHONE, phone_number
                )
                await self.verification_code_repository.delete(query)
                return None

            return code

        except Exception as e:
            logger.error(f"Error sending phone verify code: {e}")
            return None

    async def send_login_code(self, user_uuid: str, phone_number: str) -> Optional[str]:
        try:
            query = RedisQuery[VerificationCodeFields]().add_filter(
                VerificationCodeFields.PHONE, phone_number
            )
            await self.verification_code_repository.delete(query)

            code = self.verification_code_repository.gen_code()
            entity = VerificationCodeEntity(
                user_uuid=user_uuid,
                phone=phone_number,
                code=code,
                expired_at=datetime.now()
                + timedelta(seconds=self.verification_code_repository.ttl),
            )
            await self.verification_code_repository.save(entity)

            ttl_minutes = self.verification_code_repository.ttl // 60
            sent = await self.sms_api.send_login_code(
                phone_number=phone_number,
                code=code,
                time_of_live_per_minuts=ttl_minutes,
            )

            if not sent:
                query = RedisQuery[VerificationCodeFields]().add_filter(
                    VerificationCodeFields.PHONE, phone_number
                )
                await self.verification_code_repository.delete(query)
                return None

            return code

        except Exception as e:
            logger.error(f"Error sending login code: {e}")
            return None

    async def verify_code(self, code: str) -> bool:
        try:
            query = RedisQuery[VerificationCodeFields]().add_filter(
                VerificationCodeFields.CODE, code
            )
            entity = await self.verification_code_repository.get(query)

            if not entity:
                return False

            if datetime.now() > entity.expired_at:
                query = RedisQuery[VerificationCodeFields]().add_filter(
                    VerificationCodeFields.PHONE, entity.phone
                )
                await self.verification_code_repository.delete(query)
                return False

            query = RedisQuery[VerificationCodeFields]().add_filter(
                VerificationCodeFields.PHONE, entity.phone
            )
            await self.verification_code_repository.delete(query)
            return True

        except Exception as e:
            logger.error(f"Error verifying code: {e}")
            return False

    async def delete_code(self, code: str) -> bool:
        try:
            query = RedisQuery[VerificationCodeFields]().add_filter(
                VerificationCodeFields.CODE, code
            )
            entity = await self.verification_code_repository.get(query)

            if not entity:
                return False

            query = RedisQuery[VerificationCodeFields]().add_filter(
                VerificationCodeFields.PHONE, entity.phone
            )
            result = await self.verification_code_repository.delete(query)
            return result > 0

        except Exception as e:
            logger.error(f"Error deleting code: {e}")
            return False


def get_verify_service() -> VerifyService:
    return VerifyService()
