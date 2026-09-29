from ..base.exceptions import ChatError


class GroupChatError(ChatError):
    pass


class GroupChatNotFoundError(GroupChatError):
    def __init__(self, chat_uuid: str):
        self.chat_uuid = chat_uuid
        super().__init__(f"Group chat {chat_uuid} not found")


class NotFoundUser(GroupChatError):
    def __init__(self):
        super().__init__("User not found")


class ChatIsExisting(GroupChatError):
    def __init__(self):
        super().__init__("The group chat already exists")


class GroupNameRequiredError(GroupChatError):
    def __init__(self):
        super().__init__("Group name is required")


class TooFewParticipantsError(GroupChatError):
    def __init__(self, minimum: int):
        super().__init__(f"Group chat must have at least {minimum} participants")


class TooManyParticipantsError(GroupChatError):
    def __init__(self, maximum: int):
        super().__init__(f"Group chat can have at most {maximum} participants")


class UserAlreadyParticipantError(GroupChatError):
    def __init__(self, user_uuid: str):
        super().__init__(f"User {user_uuid} is already a participant")


class UserNotInGroupError(GroupChatError):
    def __init__(self, user_uuid: str):
        super().__init__(f"User {user_uuid} is not a participant of this group")


class OwnerCannotLeaveError(GroupChatError):
    def __init__(self):
        super().__init__("Owner cannot leave the group without transferring ownership")
