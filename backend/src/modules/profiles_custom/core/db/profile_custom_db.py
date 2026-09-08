from sqlalchemy.orm import InstrumentedAttribute
from src.general.db.base_manager import BaseManager

from ...models.orm.profile_custom_orm import ProfileCustomORM


class ProfileCustomManager(BaseManager[ProfileCustomORM]):
    def __init__(self):
        super().__init__(ProfileCustomORM, [ProfileCustomORM.uuid, ProfileCustomORM.updated_at])

    def identifier_field(self) -> InstrumentedAttribute:
        return ProfileCustomORM.uuid


def get_profile_custom_manager() -> ProfileCustomManager:
    return ProfileCustomManager()
