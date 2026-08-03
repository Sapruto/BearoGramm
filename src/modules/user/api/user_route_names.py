from enum import Enum
import os
from dotenv import load_dotenv, find_dotenv

from src.core.callbacks import test_url

load_dotenv(find_dotenv())

class AuthRoutes(str, Enum):
    index = '/'
    login = '/api/login'
    register = '/api/register'
    logout = '/api/logout'
    verify_phone = '/api/verify/{token}'

    def __str__(self):
        return self.value

class AuthRoutesURL(str, Enum):
    @staticmethod
    def _get_base_url() -> str:
        env = os.getenv("ENV", "development")

        if env == "production":
            base_url = os.getenv("BASE_URL")
            if not base_url:
                raise ValueError("BASE_URL must be set in .env for production")
            return base_url.rstrip('/')

        return test_url

    index = f"{_get_base_url()}{AuthRoutes.index}"
    login = f"{_get_base_url()}{AuthRoutes.login}"
    register = f"{_get_base_url()}{AuthRoutes.register}"
    logout = f"{_get_base_url()}{AuthRoutes.logout}"

    def __str__(self):
        return self.value