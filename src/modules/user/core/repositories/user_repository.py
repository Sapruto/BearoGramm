from src.general.repository.sql.sql_base_repository import BaseRepository
from typing import Optional

from .mappers.user_mapper import UserMapper
from ..db.user_db import UserManager, get_user_manager
from ...models.entities.user_entity import UserFields, UserEntity

class UserRepository(BaseRepository[UserManager, UserFields, UserEntity]):
    def __init__(self, manager: Optional[UserManager] = None):
        mapper = UserMapper()
        super().__init__(manager=manager or get_user_manager(), mapper=mapper)

def get_user_repository() -> UserRepository:
    return UserRepository()
