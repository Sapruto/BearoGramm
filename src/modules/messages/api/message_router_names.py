from enum import Enum
import os
from dotenv import load_dotenv, find_dotenv
from src.core.callbacks import test_url

class MessageRoutes(str, Enum):
    base = '/api/messages'

    send_message = '/send'
    get_messages = '/get'
    get_message = '/get'
    delete_message = '/delete'

    ws_messages = '/ws/messages'

    def __str__(self):
        return self.value

class MessageRoutesURL(str, Enum):
    @staticmethod
    def _get_base_url() -> str:
        load_dotenv(find_dotenv())
        env = os.getenv("ENV", "development")

        if env == "production":
            base_url = os.getenv("BASE_URL")
            if not base_url:
                raise ValueError("BASE_URL must be set in .env for production")
            return base_url.rstrip('/')

        return test_url

    send_message = f"{_get_base_url()}{MessageRoutes.send_message}"
    get_messages = f"{_get_base_url()}{MessageRoutes.get_messages}"
    get_message = f"{_get_base_url()}{MessageRoutes.get_message}"
    delete_message = f"{_get_base_url()}{MessageRoutes.delete_message}"
    ws_messages = f"{_get_base_url()}{MessageRoutes.ws_messages}"

    def __str__(self):
        return self.value
