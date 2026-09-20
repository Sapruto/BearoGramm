from enum import Enum

from src.core.settings import Settings


class MessageRoutes(str, Enum):
    base = "/api/messages"

    send_message = "/send"
    update_message = "/update"
    delete_message = "/delete/{message_uuid}"
    get_messages = "/get"

    ws_messages = "/ws"

    def __str__(self):
        return self.value


class MessageRoutesURL(str, Enum):
    send_message = f"{Settings.BASE_URL}{MessageRoutes.send_message}"
    update_message = f"{Settings.BASE_URL}{MessageRoutes.update_message}"
    delete_message = f"{Settings.BASE_URL}{MessageRoutes.delete_message}"
    get_messages = f"{Settings.BASE_URL}{MessageRoutes.get_messages}"
    ws_messages = (
        f"{Settings.BASE_URL}{MessageRoutes.ws_messages}"
    )

    def __str__(self):
        return self.value
