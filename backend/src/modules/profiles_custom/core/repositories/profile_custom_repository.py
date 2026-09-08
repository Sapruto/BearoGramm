from src.general.repository.sql.sql_base_repository import BaseRepository
from typing import Optional

from .mappers.profile_custom_mapper import ProfileCustomMapper
from ..db.profile_custom_db import ProfileCustomManager, get_profile_custom_manager
from ...models.entities.profile_custom_entity import ProfileCustomFields, ProfileCustomEntity


class ProfileCustomRepository(BaseRepository[ProfileCustomManager, ProfileCustomFields, ProfileCustomEntity]):
    def __init__(self, manager: Optional[ProfileCustomManager] = None):
        mapper = ProfileCustomMapper()
        super().__init__(manager=manager or get_profile_custom_manager(), mapper=mapper)


def get_profile_custom_repository() -> ProfileCustomRepository:
    return ProfileCustomRepository()
