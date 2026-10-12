from typing import Optional, Dict, List
from uuid import uuid4
from datetime import datetime, timezone

from src.core.logger import get_logger
from src.general.repository.sql.sql_query import SqlQuery

from ..exceptions import (
    ProfileCustomNotFoundError,
    ProfileCustomDataError,
    ProfileCustomAlreadyExistsError,
)
from ...models.entities.profile_custom_entity import (
    ProfileCustomEntity,
    ProfileCustomFields,
)
from ..repositories.profile_custom_repository import get_profile_custom_repository


logger = get_logger(__name__)


class ProfileCustomService:
    def __init__(self):
        self.repository = get_profile_custom_repository()

    async def create(
        self,
        user_uuid: str,
        name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> ProfileCustomEntity:
        if user_uuid:
            existing = await self.get(user_uuid=user_uuid)
            if existing:
                raise ProfileCustomAlreadyExistsError(
                    f"Profile already exists for user {user_uuid}"
                )

        entity = ProfileCustomEntity(user_uuid=user_uuid)

        if name:
            entity.name = name
        if avatar_url:
            entity.avatar_url = avatar_url

        created = await self.repository.save(entity)
        if not created:
            raise ProfileCustomDataError("Failed to save profile")

        return created

    async def update_by_user(
        self,
        user_uuid: str,
        name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> ProfileCustomEntity:
        entity = await self.get(user_uuid=user_uuid)
        if not entity:
            raise ProfileCustomNotFoundError(f"Profile for user {user_uuid} not found")

        if name is not None:
            entity.name = name
        if avatar_url is not None:
            entity.avatar_url = avatar_url
        entity.updated_at = datetime.now(timezone.utc)

        updated = await self.repository.save(entity, to_update=True)
        if not updated:
            raise ProfileCustomDataError("Failed to update profile")

        return updated

    async def delete_by_user(self, user_uuid: str) -> bool:
        entity = await self.get(user_uuid=user_uuid)
        if not entity:
            raise ProfileCustomNotFoundError(f"Profile for user {user_uuid} not found")

        query = SqlQuery[ProfileCustomFields]()
        query.add_filter(ProfileCustomFields.UUID, entity.uuid)
        deleted = await self.repository.delete(query)

        if not deleted:
            raise ProfileCustomDataError("Failed to delete profile")

        return True

    async def get(
            self,
            profile_uuid: Optional[str] = None,
            user_uuid: Optional[str] = None,
    ) -> Optional[ProfileCustomEntity]:
        query = SqlQuery[ProfileCustomFields]()
        if profile_uuid:
            query.add_filter(ProfileCustomFields.UUID, profile_uuid)
        if user_uuid:
            query.add_filter(field=ProfileCustomFields.USER_UUID, value=user_uuid)

        entity = await self.repository.get(query)
        return entity

    async def get_by_user_uuid(
        self, user_uuid: str
    ) -> Optional[ProfileCustomEntity]:
        return await self.get(user_uuid=user_uuid)

    async def get_by_user_uuids(
            self, user_uuids: List[str]
    ) -> Dict[str, ProfileCustomEntity]:
        if not user_uuids:
            return {}
    
        profiles = await self.repository.get_by_user_uuids(user_uuids)
    
        result: Dict[str, ProfileCustomEntity] = {}
        for profile in profiles:
            if profile and profile.user_uuid:
                result[profile.user_uuid] = profile
        return result


def get_profile_custom_service() -> ProfileCustomService:
    return ProfileCustomService()
