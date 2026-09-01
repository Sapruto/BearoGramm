from typing import Any, Optional


class NotConvertableError(Exception):
    pass


class NotConvertableField(NotConvertableError):
    def __init__(self, field: Any, target: str, reason: Optional[str] = None):
        self.field = field
        self.target = target
        self.reason = reason
        message = f"Field '{field}' cannot be converted to {target}"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class NotConvertableValue(NotConvertableError):
    def __init__(self, value: Any, target: str, reason: Optional[str] = None):
        self.value = value
        self.target = target
        self.reason = reason
        message = f"Value '{value}' (type: {type(value).__name__}) cannot be converted to {target}"
        if reason:
            message += f": {reason}"
        super().__init__(message)
