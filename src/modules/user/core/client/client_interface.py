from abc import ABC, abstractmethod


class ClientInterface(ABC):
    @abstractmethod
    async def send_sms(self, phone_number: str, message: str) -> bool:
        pass

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
