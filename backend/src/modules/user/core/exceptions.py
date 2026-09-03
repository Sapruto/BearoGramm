from typing import Optional


class UserException(Exception):
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class FailedToCreateUser(UserException):
    def __init__(self, phone_number: str, reason: Optional[str] = None):
        self.phone_number = phone_number
        self.reason = reason
        message = f"Failed to create user with phone {phone_number}"
        if reason:
            message += f": {reason}"
        super().__init__(message, {"phone_number": phone_number, "reason": reason})


class FailedToSendCode(UserException):
    def __init__(self, phone_number: str, user_uuid: str, reason: Optional[str] = None):
        self.phone_number = phone_number
        self.user_uuid = user_uuid
        self.reason = reason
        message = f"Failed to send code to {phone_number}"
        if reason:
            message += f": {reason}"
        super().__init__(message,
                  {"phone_number": phone_number,
                              "user_uuid": user_uuid,
                              "reason": reason
                         }
        )


class FailedToGetLoginToken(UserException):
    def __init__(self, phone_number: str, reason: Optional[str] = None):
        self.phone_number = phone_number
        self.reason = reason
        message = f"Failed to get login token for {phone_number}"
        if reason:
            message += f": {reason}"
        super().__init__(message, {"phone_number": phone_number, "reason": reason})


class InvalidOrExpiredCode(UserException):
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        super().__init__(
            f"Invalid or expired code for {phone_number}",
            {"phone_number": phone_number}
        )


class UserNotFound(UserException):
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        super().__init__(
            f"User with phone {phone_number} not found",
            {"phone_number": phone_number}
        )


class VerificationFailed(UserException):
    def __init__(self, phone_number: str, reason: Optional[str] = None):
        self.phone_number = phone_number
        self.reason = reason
        message = f"Verification failed for {phone_number}"
        if reason:
            message += f": {reason}"
        super().__init__(message, {"phone_number": phone_number, "reason": reason})


class InvalidPhoneNumber(UserException):
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        super().__init__(
            f"Invalid phone number format: {phone_number}",
            {"phone_number": phone_number}
        )


class SessionCreationFailed(UserException):
    def __init__(self, user_uuid: str, reason: Optional[str] = None):
        self.user_uuid = user_uuid
        self.reason = reason
        message = f"Failed to create session for user {user_uuid}"
        if reason:
            message += f": {reason}"
        super().__init__(message, {"user_uuid": user_uuid, "reason": reason})
