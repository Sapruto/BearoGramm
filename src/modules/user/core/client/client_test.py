from src.core.logger import get_logger
from .client_interface import ClientInterface

logger = get_logger(__name__)


class ClientTest(ClientInterface):
    async def send_sms(self, phone_number: str, message: str) -> bool:
        try:
            logger.info(f"Sending SMS REALY: {phone_number}, Messages: {message}")
            return True
        except Exception as e:
            logger.error(
                f"Error sending SMS to {phone_number} after {self.max_retries} retries: {e}",
                exc_info=True,
            )
            return False


def get_client_smsru() -> ClientTest:
    return ClientTest()
