from ..base.exceptions import ChatError

class PersonalChatError(ChatError):
    pass

class PersonalChatNotFoundError(PersonalChatError):
    def __init__(self, chat_uuid: str):
        self.chat_uuid = chat_uuid
        super().__init__(f"Personal chat {chat_uuid} not found")

class CannotChatWithSelfError(PersonalChatError):
    def __init__(self):
        super().__init__("You can't start a chat with yourself")

class NotFoundUser(PersonalChatError):
    def __init__(self):
        super().__init__("User not found")

class ChatIsExisting(PersonalChatError):
    def __init__(self):
        super().__init__("The chat already exists")
