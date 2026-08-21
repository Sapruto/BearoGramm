import os
from smsru_api import AsyncClient

from src.core.logger import get_logger

logger = get_logger(__name__)

class ClientSMSRu:
    def __init__(self):
        self.api_key = os.getenv("SMS_RU_API_KEY")
        if not self.api_key:
            raise ValueError("SMS_RU_API_KEY must be in the env.")

        self._client = AsyncClient(api_key=self.api_key) if self.api_key else None

    async def send_sms(self, phone_number: str, message: str) -> bool:
        try:
            if not self._client:
                logger.error("SMS client not initialized")
                return False

            response = await self._client.send_sms(
                phone=phone_number,
                message=message
            )

            if response and response.get("status") == "OK":
                return True
            else:
                logger.error(f"SMS sending failed: {response}")
                return False

        except Exception as e:
            logger.error(f"Error sending SMS to {phone_number}: {e}", exc_info=True)
            return False

    async def send_verify_code(self, phone_number: str, code: str, time_of_live_per_minuts: int) -> bool:
        message = f"Ваш код подтверждения: {code}. Действителен {time_of_live_per_minuts} минут."
        return await self.send_sms(phone_number, message)

    async def send_login_code(self, phone_number: str, code: str, time_of_live_per_minuts: int) -> bool:
        message = f"Код для входа: {code}. Действителен {time_of_live_per_minuts} минут."
        return await self.send_sms(phone_number, message)

def get_client_smsru() -> ClientSMSRu:
    return ClientSMSRu()
