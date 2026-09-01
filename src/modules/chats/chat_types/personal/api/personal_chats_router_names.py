from enum import Enum

from src.core.settings import Settings


class PersonalChatsRoutes(str, Enum):
    base = "/personal/chats"
    create = "/create"
    get = "/{chat_uuid}"
    list = "/list"
    contacts = "/contacts"
    find = "/find"
    add_user = "/{chat_uuid}/users"
    remove_user = "/{chat_uuid}/users/{user_uuid}"
    block = "/{chat_uuid}/block"
    unblock = "/{chat_uuid}/unblock"
    delete = "/{chat_uuid}"

    def __str__(self):
        return self.value


class PersonalChatsRoutesURL(str, Enum):
    create = f"{Settings.BASE_URL}{PersonalChatsRoutes.create}"
    get = f"{Settings.BASE_URL}{PersonalChatsRoutes.get}"
    list = f"{Settings.BASE_URL}{PersonalChatsRoutes.list}"
    contacts = f"{Settings.BASE_URL}{PersonalChatsRoutes.contacts}"
    find = f"{Settings.BASE_URL}{PersonalChatsRoutes.find}"
    add_user = f"{Settings.BASE_URL}{PersonalChatsRoutes.add_user}"
    remove_user = f"{Settings.BASE_URL}{PersonalChatsRoutes.remove_user}"
    block = f"{Settings.BASE_URL}{PersonalChatsRoutes.block}"
    unblock = f"{Settings.BASE_URL}{PersonalChatsRoutes.unblock}"
    delete = f"{Settings.BASE_URL}{PersonalChatsRoutes.delete}"

    def __str__(self):
        return self.value
