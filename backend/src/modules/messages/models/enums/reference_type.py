from enum import Enum


class ReferenceType(str, Enum):
    ANSWER = "answer"
    REMEMBER = "remember"
    QUOTE = "quote"

    def __str__(self):
        return self.value
