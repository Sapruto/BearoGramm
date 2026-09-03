from enum import Enum

from src.core.settings import Settings


class CallsRoutes(str, Enum):
    base = "/api/calls"

    call = "/ws/call"
    listen_calls = "ws/listen_calls"

    def __str__(self):
        return self.value


class CallsRoutesURL(str, Enum):
    call = f"{Settings.BASE_URL}{CallsRoutes.call}"
    listen_calls = f"{Settings.BASE_URL}{CallsRoutes.listen_calls}"

    def __str__(self):
        return self.value
