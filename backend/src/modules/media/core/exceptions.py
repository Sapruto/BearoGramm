class MessageServiceError(Exception):
    pass


class StorageError(MessageServiceError):
    pass


class NotFoundError(MessageServiceError):
    pass
