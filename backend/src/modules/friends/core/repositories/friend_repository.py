from src.general.repository.sql.sql_base_repository import BaseRepository
from typing import Optional

from .mappers.friend_mapper import FriendMapper
from ..db.friend_db import FriendManager, get_friend_manager
from ...models.entities.friend_entity import FriendFields, FriendEntity


class FriendRepository(BaseRepository[FriendManager, FriendFields, FriendEntity]):
    def __init__(self, manager: Optional[FriendManager] = None):
        super().__init__(manager=manager or get_friend_manager(), mapper=FriendMapper())


def get_friend_repository() -> FriendRepository:
    return FriendRepository()
