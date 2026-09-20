from typing import Annotated, Literal, Union, Dict, List
from pydantic import BaseModel, Field, computed_field

from src.core.settings import Settings
from .enums.extra_data_type import ExtraDataType


class BaseExtraData(BaseModel):
    extra_data_type: ExtraDataType

    @classmethod
    def sensitive_fields(cls) -> List[str]:
        return []


class PollExtraData(BaseExtraData):
    extra_data_type: Literal[ExtraDataType.POLL] = ExtraDataType.POLL
    question: str
    options: List[str]
    multi: bool = False
    anonymous: bool = True

    @classmethod
    def sensitive_fields(cls) -> List[str]:
        return ["question", "options"]


class InlineKeyboardExtraData(BaseExtraData):
    extra_data_type: Literal[ExtraDataType.INLINE_KEYBOARD] = ExtraDataType.INLINE_KEYBOARD
    rows: List[List[Dict]] = Field(default_factory=list)
    # WHAT TAK NADO EPTA: [[{"text": "...", ...}], ...]

    @classmethod
    def sensitive_fields(cls) -> List[str]:
        return ["rows"]


class ReactionsExtraData(BaseExtraData):
    extra_data_type: Literal[ExtraDataType.REACTIONS] = ExtraDataType.REACTIONS
    allowed: List[str] = Field(default_factory=list)


class EmbedExtraData(BaseExtraData):
    extra_data_type: Literal[ExtraDataType.EMBED] = ExtraDataType.EMBED
    url: str
    title: str | None = None
    description: str | None = None
    image: str | None = None

    @classmethod
    def sensitive_fields(cls) -> list[str]:
        return ["title", "description"]


class CustomExtraData(BaseExtraData):
    extra_data_type: Literal[ExtraDataType.CUSTOM] = ExtraDataType.CUSTOM
    data: Dict = Field(default_factory=dict)

    @classmethod
    def sensitive_fields(cls) -> list[str]:
        return ["data"]


class MediaExtraData(BaseExtraData):
    extra_data_type: Literal[ExtraDataType.MEDIA] = ExtraDataType.MEDIA
    media_uuid: str

    @computed_field
    @property
    def url(self) -> str:
        return f"{Settings.MEDIA_BASE_URL}/{self.media_uuid}"


ExtraData = Annotated[
    Union[
        PollExtraData,
        InlineKeyboardExtraData,
        ReactionsExtraData,
        EmbedExtraData,
        CustomExtraData,
        MediaExtraData,
    ],
    Field(discriminator="extra_data_type"),
]
