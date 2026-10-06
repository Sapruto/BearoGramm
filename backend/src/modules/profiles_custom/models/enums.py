from enum import Enum


class BannerColor(str, Enum):
    DEFAULT = "default"
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    HEX = "hex"

    def __str__(self):
        return self.value


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
