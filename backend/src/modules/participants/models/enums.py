from enum import Enum
from typing import Union


class ResourceType(str, Enum):
    CHAT = "chat"
    MESSAGE = "message"
    FILE = "file"
    CHANNEL = "channel"

    def __str__(self):
        return self.value


class ActionCategory(str, Enum):
    CHAT = "chat"
    MESSAGE = "message"
    FILE = "file"
    CHANNEL = "channel"

    def __str__(self):
        return self.value


class ChatAction(str, Enum):
    KICK = "kick"
    MANAGE = "manage"
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    GET = "view"
    LOCK = "lock"
    UNLOCK = "unlock"
    ARCHIVE = "archive"
    RESTORE = "restore"
    MUTE = "mute"
    UNMUTE = "unmute"
    INVITE = "invite"
    REMOVE = "remove"

    def __str__(self):
        return self.value


class MessageAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    GET = "get"

    def __str__(self):
        return self.value


class FileAction(str, Enum):
    UPLOAD = "upload"
    DOWNLOAD = "download"
    DELETE = "delete"
    UPDATE = "update"
    VIEW = "view"
    SHARE = "share"
    UNSHARE = "unshare"
    MOVE = "move"
    COPY = "copy"
    RENAME = "rename"

    def __str__(self):
        return self.value


class ChannelAction(str, Enum):
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    VIEW = "view"
    MANAGE = "manage"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    BROADCAST = "broadcast"
    MUTE = "mute"
    UNMUTE = "unmute"

    def __str__(self):
        return self.value


class ActionType:
    CHAT = ChatAction
    MESSAGE = MessageAction
    FILE = FileAction
    CHANNEL = ChannelAction

    @classmethod
    def get_action(cls, category: ActionCategory, action: str) -> Enum:
        mapping = {
            ActionCategory.CHAT: cls.CHAT,
            ActionCategory.MESSAGE: cls.MESSAGE,
            ActionCategory.FILE: cls.FILE,
            ActionCategory.CHANNEL: cls.CHANNEL,
        }
        enum_class = mapping.get(category)
        if not enum_class:
            raise ValueError(f"Unknown category: {category}")
        return enum_class(action)

    @classmethod
    def get_category(cls, action: Enum) -> ActionCategory:
        if isinstance(action, cls.CHAT):
            return ActionCategory.CHAT
        elif isinstance(action, cls.MESSAGE):
            return ActionCategory.MESSAGE
        elif isinstance(action, cls.FILE):
            return ActionCategory.FILE
        elif isinstance(action, cls.CHANNEL):
            return ActionCategory.CHANNEL
        raise ValueError(f"Unknown action type: {type(action)}")


class PermissionType(str, Enum):
    CHAT = "chat"
    MESSAGE = "message"
    FILE = "file"
    CHANNEL = "channel"

    def __str__(self):
        return self.value

ActionTypification = Union[ChatAction, MessageAction, FileAction, ChannelAction]
