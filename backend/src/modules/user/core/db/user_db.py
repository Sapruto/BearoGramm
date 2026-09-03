from sqlalchemy.orm import InstrumentedAttribute

from src.general.db.base_manager import BaseManager

from ...models.orm.user_orm import UserORM


class UserManager(BaseManager[UserORM]):
    def __init__(self):
        super().__init__(UserORM, [UserORM.uuid, UserORM.created_at])

    @property
    def identifier_field(self) -> InstrumentedAttribute:
        return UserORM.uuid


def get_user_manager() -> UserManager:
    return UserManager()
