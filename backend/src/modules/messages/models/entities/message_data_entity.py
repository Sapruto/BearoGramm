from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from ..enums.extra_data_type import ExtraDataType
from ..extra_data import ExtraData


class MessageDataFields(str, Enum):
    MESSAGE_UUID = "message_uuid"
    EXTRA_DATA_TYPE = "extra_data_type"
    PAYLOAD = "payload"
    SCHEMA_VERSION = "schema_version"

    def __str__(self):
        return self.value


class MessageDataEntity(BaseModel):
    message_uuid: Optional[str] = Field(default=None)
    extra_data_type: ExtraDataType
    payload: ExtraData
    schema_version: int = Field(default=1)

    @model_validator(mode="after")
    def _check_type_matches_payload(self) -> "MessageDataEntity":
        if self.payload.extra_data_type != self.extra_data_type:
            raise ValueError(
                f"extra_data_type={self.extra_data_type.value!r} "
                f"does not match payload.extra_data_type="
                f"{self.payload.extra_data_type.value!r}"
            )
        return self
