from sqlalchemy import or_

from src.general.repository.sql.sql_base_repository import BaseRepository
from typing import Optional, List

from .mappers.profile_custom_mapper import ProfileCustomMapper
from ..db.profile_custom_db import ProfileCustomManager, get_profile_custom_manager
from ...models.entities.profile_custom_entity import ProfileCustomFields, ProfileCustomEntity
from ...models.orm.profile_custom_orm import ProfileCustomORM


class ProfileCustomRepository(BaseRepository[ProfileCustomManager, ProfileCustomFields, ProfileCustomEntity]):
    def __init__(self, manager: Optional[ProfileCustomManager] = None):
        mapper = ProfileCustomMapper()
        super().__init__(manager=manager or get_profile_custom_manager(), mapper=mapper)

    async def get_by_user_uuids(self, user_uuids: List[str]) -> List[ProfileCustomEntity]:
        if not user_uuids:
            return []

        conditions = [ProfileCustomORM.user_uuid == uid for uid in user_uuids]
        orms = await self.manager.get_all(
            where=or_(*conditions) if len(conditions) > 1 else conditions[0]
        )

        return [self._to_entity(orm) for orm in orms]


def get_profile_custom_repository() -> ProfileCustomRepository:
    return ProfileCustomRepository()
