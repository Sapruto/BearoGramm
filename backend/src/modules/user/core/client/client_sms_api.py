from typing import Optional
from src.core.settings import Settings
from src.core.logger import get_logger

from .client_interface import ClientInterface

logger = get_logger(__name__)


def _get_client() -> ClientInterface:
    from .client_test import ClientTest
    from .client_sms_ru import ClientSMSRu

    if Settings.ENV == "test":
        return ClientTest()
    elif Settings.ENV == "sms_ru":
        return ClientSMSRu()
    return ClientTest()


class ClientSMS:
    def __init__(self, sms_client: Optional[ClientInterface] = None):
        self.sms_client = sms_client or _get_client()

    async def send_verify_code(
        self, phone_number: str, code: str, time_of_live_per_minuts: int
    ) -> bool:
        return await self.sms_client.send_verify_code(
            phone_number, code, time_of_live_per_minuts
        )

    async def send_login_code(
        self, phone_number: str, code: str, time_of_live_per_minuts: int
    ) -> bool:
        return await self.sms_client.send_login_code(
            phone_number, code, time_of_live_per_minuts
        )

    async def send_custom_sms(self, phone_number: str, message: str) -> bool:
        return await self.sms_client.send_sms(phone_number, message)


def get_client_sms_api() -> ClientSMS:
    return ClientSMS()
