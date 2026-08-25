from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from typing import Optional, List, Any
from datetime import datetime

from ...chat_types.base.base_access_type import definite_access_type

class ChatFields(str, Enum):
    UUID = "uuid"

    ACCESSES = "accesses"

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"

    def __str__(self):
        return self.value

class ChatEntity(BaseModel):
    uuid: Optional[str] = Field(default=None)

    accesses: List[definite_access_type] = Field(default_factory=list)

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    @property
    def access_type(self) -> str:
        if not self.accesses:
            return ""

        try:
            first_access = self.accesses[0]
            if hasattr(first_access, 'get_type'):
                access_obj = first_access.get_type()
                if hasattr(access_obj, 'get_type'):
                    return access_obj.get_type()
        except Exception:
            pass

        return ""

    @field_validator('accesses')
    @classmethod
    def validate_accesses(cls, v: Any) -> List[definite_access_type]:
        if not v:
            return []

        if not isinstance(v, list):
            raise ValueError("accesses must be a list")

        for access in v:
            if not hasattr(access, 'get_type'):
                raise ValueError(f"Invalid access type: {access}")

        return v

    @model_validator(mode='after')
    def validate_chat(self) -> 'ChatEntity':
        min_users_in_chat = 1
        if len(self.accesses) < min_users_in_chat:
            raise ValueError(f"accesses can't be < {min_users_in_chat}")

        return self

    def add_access(self, access: definite_access_type) -> None:
        self.accesses.append(access)

    def remove_access(self, access: definite_access_type) -> None:
        if access in self.accesses:
            self.accesses.remove(access)
