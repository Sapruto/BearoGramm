from enum import Enum


class ChatType(str, Enum):
    PERSONAL = "personal"
    GROUP = "group"
    CHANNEL = "channel"
    DEFAULT = "default"

    def __str__(self):
        return self.value
