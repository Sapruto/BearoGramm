from enum import Enum

from src.core.settings import Settings


class AuthRoutes(str, Enum):
    base = "/api/auth"
    send_code = "/send_verify_code"
    verify_phone = "/verify_phone"

    def __str__(self):
        return self.value


class AuthRoutesURL(str, Enum):
    send_code = f"{Settings.BASE_URL}{AuthRoutes.send_code}"
    verify_phone = f"{Settings.BASE_URL}{AuthRoutes.verify_phone}"

    def __str__(self):
        return self.value
