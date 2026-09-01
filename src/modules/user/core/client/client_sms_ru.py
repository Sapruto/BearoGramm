import asyncio
from smsru_api import AsyncClient

from src.core.settings import Settings
from src.core.logger import get_logger

logger = get_logger(__name__)


class ClientSMSRu:
    def __init__(self, max_retries: int = 3, retry_delay: int = 1):
        self.api_key = Settings.PHONE.ASYNC_CLIENT_API_ID
        if not self.api_key:
            raise ValueError("ASYNC_CLIENT_API_ID must be in the env.")

        self._client = AsyncClient(api_id=self.api_key) if self.api_key else None
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def _send_with_retry(self, phone_number: str, message: str) -> dict:
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                if not self._client:
                    raise ValueError("SMS client not initialized")

                logger.debug(
                    f"Attempt {attempt}/{self.max_retries} to send SMS to {phone_number}"
                )

                response = await self._client.send(
                    numbers=phone_number, message=message
                )

                if response and response.get("status") == "OK":
                    logger.info(f"SMS sent successfully on attempt {attempt}")
                    return response
                else:
                    error_msg = f"API returned error: {response}"
                    logger.warning(f"Attempt {attempt} failed: {error_msg}")
                    last_error = Exception(error_msg)

            except Exception as e:
                logger.warning(f"Attempt {attempt} failed with exception: {e}")
                last_error = e

            if attempt < self.max_retries:
                wait_time = self.retry_delay * attempt
                logger.debug(f"Waiting {wait_time}s before next attempt...")
                await asyncio.sleep(wait_time)

        raise last_error or Exception("All retry attempts failed")

    async def send_sms(self, phone_number: str, message: str) -> bool:
        try:
            await self._send_with_retry(phone_number, message)
            return True
        except Exception as e:
            logger.error(
                f"Error sending SMS to {phone_number} after {self.max_retries} retries: {e}",
                exc_info=True,
            )
            return False

    async def send_verify_code(
        self, phone_number: str, code: str, time_of_live_per_minuts: int
    ) -> bool:
        message = f"Ваш код подтверждения: {code}. Действителен {time_of_live_per_minuts} минут."
        return await self.send_sms(phone_number, message)

    async def send_login_code(
        self, phone_number: str, code: str, time_of_live_per_minuts: int
    ) -> bool:
        message = (
            f"Код для входа: {code}. Действителен {time_of_live_per_minuts} минут."
        )
        return await self.send_sms(phone_number, message)


def get_client_smsru() -> ClientSMSRu:
    return ClientSMSRu()
