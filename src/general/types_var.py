from pydantic import BaseModel
from typing import TypeVar
from enum import Enum

from src.core.database import Base

Manager = TypeVar("Manager", bound='BaseManager')
Fields = TypeVar("Fields", bound=Enum)
Entity = TypeVar("Entity", bound=BaseModel)
ORM = TypeVar("ORM", bound=Base)