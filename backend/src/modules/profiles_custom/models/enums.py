from enum import Enum


class Gender(str, Enum):
    BEAR = "bear"
    MAN = "man"
    WOMAN = "woman"

    AMEBA = "ameba"
    TROLL_FACE = "troll_face"
    COMMUNIST = "communist"
    COCK = "cock"

    def __str__(self):
        return self.value
