from pydantic import BaseModel
from typing import Generic
from ...types_var import Fields


class QueryInterface(BaseModel, Generic[Fields]):
    pass
