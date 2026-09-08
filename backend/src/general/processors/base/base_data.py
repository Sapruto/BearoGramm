from pydantic import BaseModel
from typing import TypeVar


class BaseData(BaseModel):
    data_type: str


base_data_type = TypeVar("base_data_type", bound=BaseData)
