from enum import Enum
import os
from dotenv import load_dotenv, find_dotenv
from src.core.callbacks import test_url

class MessageRoutes(str, Enum):
    base = '/api/messages'

    send_message = '/send'
    update_message = '/update'
    delete_message = '/delete'
    get_messages = '/get'

    listen_messages_websocket = '/ws/listen_messages_websocket'

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
            return base_url.rstrip('/') + MessageRoutes.base

        return test_url + MessageRoutes.base

    send_message = f"{_get_base_url()}{MessageRoutes.send_message}"
    update_message = f"{_get_base_url()}{MessageRoutes.update_message}"
    delete_message = f"{_get_base_url()}{MessageRoutes.delete_message}"
    get_messages = f"{_get_base_url()}{MessageRoutes.get_messages}"
    listen_messages_websocket = f"{_get_base_url()}{MessageRoutes.listen_messages_websocket}"

    def __str__(self):
        return self.value
