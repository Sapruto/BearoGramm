class PermissionError(Exception):
    pass


class PermissionNotFoundError(PermissionError):
    pass


class ParticipantNotFoundError(PermissionError):
    pass


class PermissionAlreadyExistsError(PermissionError):
    pass


class InvalidPermissionTypeError(PermissionError):
    pass


class ResourceNotFoundError(PermissionError):
    pass
