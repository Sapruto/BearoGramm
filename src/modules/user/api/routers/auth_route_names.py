from enum import Enum

from src.core.settings import Settings


class AuthRoutes(str, Enum):
    base = "/api/auth"
    get_login_token = "/get_login_token"
    verify_phone = "/verify_phone"

    def __str__(self):
        return self.value


class AuthRoutesURL(str, Enum):
    get_login_token = f"{Settings.BASE_URL}{AuthRoutes.get_login_token}"
    verify_phone = f"{Settings.BASE_URL}{AuthRoutes.verify_phone}"

    def __str__(self):
        return self.value
