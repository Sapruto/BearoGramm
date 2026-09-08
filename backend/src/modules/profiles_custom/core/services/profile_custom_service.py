from typing import Optional, Dict, Any, List
from uuid import uuid4

from sqlalchemy import or_

from src.general.processors.data_processor import DataProcessor
from src.general.repository.sql.sql_query import SqlQuery

from ..exceptions import (
    ProfileCustomNotFoundError,
    ProfileCustomDataError,
    ProfileCustomAlreadyExistsError,
)
from ...models.entities.profile_custom_entity import ProfileCustomEntity, ProfileCustomFields
from ..repositories.profile_custom_repository import get_profile_custom_repository


class ProfileCustomService:
    def __init__(self):
        self.repository = get_profile_custom_repository()
        self.data_processor = DataProcessor()

    async def create(
        self,
        data: Dict[str, Any],
        user_uuid: Optional[str] = None,
        profile_uuid: Optional[str] = None,
    ) -> ProfileCustomEntity:
        try:
            if user_uuid:
                query = SqlQuery[ProfileCustomFields]()
                query.add_filter(ProfileCustomFields.USER_UUID, user_uuid)
                existing = await self.repository.get(query)
                if existing:
                    raise ProfileCustomAlreadyExistsError(f"Profile already exists for user {user_uuid}")

            entity = ProfileCustomEntity(
                uuid=profile_uuid or str(uuid4()),
                data=data,
                user_uuid=user_uuid,
            )

            created = await self.repository.save(entity)
            if not created:
                raise ProfileCustomDataError("Failed to save profile")

            return created

        except Exception:
            raise

    async def get(
        self,
        profile_uuid: Optional[str] = None,
        user_uuid: Optional[str] = None,
    ) -> Optional[ProfileCustomEntity]:
        query = SqlQuery[ProfileCustomFields]()
        if profile_uuid:
            query.add_filter(ProfileCustomFields.UUID, profile_uuid)
        if user_uuid:
            query.add_filter(ProfileCustomFields.USER_UUID, user_uuid)
        return await self.repository.get(query)

    async def update_by_user(
        self,
        user_uuid: str,
        data: Dict[str, Any],
    ) -> ProfileCustomEntity:
        entity = await self.get(user_uuid=user_uuid)
        if not entity:
            raise ProfileCustomNotFoundError(f"Profile for user {user_uuid} not found")

        entity.data = data

        updated = await self.repository.update(entity)
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

        if deleted == 0:
            raise ProfileCustomDataError("Failed to delete profile")

        return True

    async def get_by_user_uuids(
            self,
            user_uuids: List[str],
    ) -> Dict[str, ProfileCustomEntity]:
        profiles = await self.repository.get_by_user_uuids(user_uuids)

        result = {}
        for profile in profiles:
            if profile.user_uuid:
                result[profile.user_uuid] = profile

        return result


def get_profile_custom_service() -> ProfileCustomService:
    return ProfileCustomService()
