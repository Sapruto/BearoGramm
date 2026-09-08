from pydantic import BaseModel, Field
from enum import Enum

from datetime import datetime
from typing import List, Optional

from src.general.processors.base.base_data import base_data_type


class ProfileCustomFields(str, Enum):
    UUID = "uuid"
    DATA = "data"
    UPDATED_AT = "updated_at"
    USER_UUID = "user_uuid"

    def __str__(self):
        return self.value


class ProfileCustomEntity(BaseModel):
    uuid: Optional[str] = Field(default=None)

    data: List[base_data_type] = Field(default=[])

    updated_at: Optional[datetime] = Field(default=None)

    user_uuid: Optional[str] = Field(default=None)

    def add_data(self, new_data: base_data_type) -> None:
        self.data.append(new_data)

    def remove_data(self, delete_data: base_data_type) -> None:
        if delete_data in self.data:
            self.data.remove(delete_data)

    def update_data(self, index: int, new_data: base_data_type) -> None:
        if 0 <= index < len(self.data):
            self.data[index] = new_data
