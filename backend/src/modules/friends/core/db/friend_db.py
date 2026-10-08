from sqlalchemy.orm import InstrumentedAttribute

from src.general.db.base_manager import BaseManager

from ...models.orm.friend_orm import FriendORM


class FriendManager(BaseManager[FriendORM]):
    def __init__(self):
        super().__init__(FriendORM, [FriendORM.uuid, FriendORM.created_at])

    @property
    def identifier_field(self) -> InstrumentedAttribute:
        return FriendORM.uuid


def get_friend_manager() -> FriendManager:
    return FriendManager()
