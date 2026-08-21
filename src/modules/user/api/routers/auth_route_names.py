from enum import Enum
import os
from dotenv import load_dotenv, find_dotenv

from src.core.callbacks import test_url

load_dotenv(find_dotenv())

class AuthRoutes(str, Enum):
    get_login_token = '/api/auth/get_login_token'
    verify_phone = '/api/auth/verify_phone'

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

    get_login_token = f"{_get_base_url()}{AuthRoutes.get_login_token}"
    verify_phone = f"{_get_base_url()}{AuthRoutes.verify_phone}"

    def __str__(self):
        return self.value
