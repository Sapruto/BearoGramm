class MessageException(Exception):
    pass


class ChecksFailed(MessageException):
    def __init__(self, message: str = "You don't have permission to perform this action on the chat"):
        super().__init__(message)


class FailedToProcessData(MessageException):
    def __init__(self, message: str = "Failed to process message data"):
        super().__init__(message)


class DatabaseSaveFailed(MessageException):
    def __init__(self, message: str = "Failed to save message to the database"):
        super().__init__(message)


class MessageNotFoundError(MessageException):
    def __init__(self, message: str = "Message not found"):
        super().__init__(message)


class MessageNotOwnedByUserError(MessageException):
    def __init__(self, message: str = "Message does not belong to this user"):
        super().__init__(message)


class DatabaseUpdateFailed(MessageException):
    def __init__(self, message: str = "Failed to update message in the database"):
        super().__init__(message)


class DatabaseDeleteFailed(MessageException):
    def __init__(self, message: str = "Failed to delete message from the database"):
        super().__init__(message)
