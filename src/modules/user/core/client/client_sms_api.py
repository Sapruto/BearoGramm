from typing import Optional
from .client_sms_ru import ClientSMSRu, get_client_smsru
from src.core.logger import get_logger

logger = get_logger(__name__)

class ClientSMS:
    def __init__(self, sms_client: Optional[ClientSMSRu] = None):
        self.sms_client = sms_client or get_client_smsru()

    async def send_verify_code(self, phone_number: str, code: str, time_of_live_per_minuts: int) -> bool:
        return await self.sms_client.send_verify_code(phone_number, code, time_of_live_per_minuts)

    async def send_login_code(self, phone_number: str, code: str, time_of_live_per_minuts: int) -> bool:
        return await self.sms_client.send_login_code(phone_number, code, time_of_live_per_minuts)

    async def send_custom_sms(self, phone_number: str, message: str) -> bool:
        return await self.sms_client.send_sms(phone_number, message)

def get_client_sms_api() -> ClientSMS:
    return ClientSMS()
