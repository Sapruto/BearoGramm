from enum import Enum


class ExtraDataType(str, Enum):
    POLL = "poll"
    INLINE_KEYBOARD = "inline_keyboard"
    REACTIONS = "reactions"
    EMBED = "embed"
    CUSTOM = "custom"
    MEDIA = "media"

    def __str__(self):
        return self.value
