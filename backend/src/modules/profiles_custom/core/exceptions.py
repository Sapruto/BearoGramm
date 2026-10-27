class ProfileCustomError(Exception):
    pass


class ProfileCustomNotFoundError(ProfileCustomError):
    pass

class BadAvatarUrl(ProfileCustomError):
    pass


class ProfileCustomValidationError(ProfileCustomError):
    pass


class ProfileCustomDataError(ProfileCustomError):
    pass


class ProfileCustomAlreadyExistsError(ProfileCustomError):
    pass


class NotFoundProfile(ProfileCustomError):
    pass
