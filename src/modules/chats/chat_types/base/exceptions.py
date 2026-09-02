class ChatError(Exception):
    pass


class ChatNotFoundError(ChatError):
    def __init__(self, chat_uuid: str):
        self.chat_uuid = chat_uuid
        super().__init__(f"Chat {chat_uuid} not found")


class UserNotParticipantError(ChatError):
    def __init__(self, user_uuid: str, chat_uuid: str):
        self.user_uuid = user_uuid
        self.chat_uuid = chat_uuid
        super().__init__(f"User {user_uuid} is not a participant of chat {chat_uuid}")


class PermissionDeniedError(ChatError):
    def __init__(self, user_uuid: str, action: str, resource_uuid: str):
        self.user_uuid = user_uuid
        self.action = action
        self.resource_uuid = resource_uuid
        super().__init__(f"User {user_uuid} has no {action} permission on {resource_uuid}")


class CreatorMustBeParticipantError(ChatError):
    def __init__(self):
        super().__init__("Creator must be in participants list")


class DuplicateParticipantsError(ChatError):
    def __init__(self):
        super().__init__("Duplicate participants not allowed")


class InvalidParticipantsError(ChatError):
    def __init__(self, message: str):
        super().__init__(message)
