from enum import Enum

class MessageActionType(str, Enum):
    CREATE = "create_message"
    UPDATE = "update_message"
    DELETE = "delete_message"
    GET = "get_message"
