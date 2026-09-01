from pydantic import BaseModel
from ..enums import ActionTypification

class Permission(BaseModel):
    action: ActionTypification
    enabled: bool = True
