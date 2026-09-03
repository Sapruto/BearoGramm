from ..base.exceptions import ChatError

class PersonalChatError(ChatError):
    pass

class PersonalChatNotFoundError(PersonalChatError):
    def __init__(self, chat_uuid: str):
        self.chat_uuid = chat_uuid
        super().__init__(f"Personal chat {chat_uuid} not found")

class CannotChatWithSelfError(PersonalChatError):
    def __init__(self):
        super().__init__("Cannot create personal chat with yourself")

class NotFoundUser(PersonalChatError):
    def __init__(self):
        super().__init__("Not found user by phone.")
