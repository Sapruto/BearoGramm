from enum import Enum
import os
from dotenv import load_dotenv, find_dotenv
from src.core.callbacks import test_url

class CallsRoutes(str, Enum):
    base = '/api/calls'

    call = '/ws/call'
    listen_calls = 'ws/listen_calls'

    def __str__(self):
        return self.value

class CallsRoutesURL(str, Enum):
    @staticmethod
    def _get_base_url() -> str:
        load_dotenv(find_dotenv())
        env = os.getenv("ENV", "development")

        if env == "production":
            base_url = os.getenv("BASE_URL")
            if not base_url:
                raise ValueError("BASE_URL must be set in .env for production")
            return base_url.rstrip('/') + CallsRoutes.base

        return test_url + CallsRoutes.base

    call = f"{_get_base_url()}{CallsRoutes.call}"
    listen_calls = f"{_get_base_url()}{CallsRoutes.listen_calls}"

    def __str__(self):
        return self.value
