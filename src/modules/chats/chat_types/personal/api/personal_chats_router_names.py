from enum import Enum
import os
from dotenv import load_dotenv, find_dotenv

from src.core.callbacks import test_url

load_dotenv(find_dotenv())

class PersonalChatsRoutes(str, Enum):
    base = '/personal/chats'
    create = '/create'
    get = '/{chat_uuid}'
    list = '/list'
    contacts = '/contacts'
    find = '/find'
    add_user = '/{chat_uuid}/users'
    remove_user = '/{chat_uuid}/users/{user_uuid}'
    block = '/{chat_uuid}/block'
    unblock = '/{chat_uuid}/unblock'
    delete = '/{chat_uuid}'

    def __str__(self):
        return self.value

class PersonalChatsRoutesURL(str, Enum):
    @staticmethod
    def _get_base_url() -> str:
        env = os.getenv("ENV", "development")

        if env == "production":
            base_url = os.getenv("BASE_URL")
            if not base_url:
                raise ValueError("BASE_URL must be set in .env for production")
            return base_url.rstrip('/')

        return test_url

    create = f"{_get_base_url()}{PersonalChatsRoutes.create}"
    get = f"{_get_base_url()}{PersonalChatsRoutes.get}"
    list = f"{_get_base_url()}{PersonalChatsRoutes.list}"
    contacts = f"{_get_base_url()}{PersonalChatsRoutes.contacts}"
    find = f"{_get_base_url()}{PersonalChatsRoutes.find}"
    add_user = f"{_get_base_url()}{PersonalChatsRoutes.add_user}"
    remove_user = f"{_get_base_url()}{PersonalChatsRoutes.remove_user}"
    block = f"{_get_base_url()}{PersonalChatsRoutes.block}"
    unblock = f"{_get_base_url()}{PersonalChatsRoutes.unblock}"
    delete = f"{_get_base_url()}{PersonalChatsRoutes.delete}"

    def __str__(self):
        return self.value
