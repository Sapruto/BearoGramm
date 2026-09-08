from typing import Optional, List, Tuple, Any
from uuid import uuid4

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
        typing_to_data: List[Tuple[str, Any]],
        user_uuid: Optional[str] = None,
        profile_uuid: Optional[str] = None,
    ) -> ProfileCustomEntity:
        process_result = await self.data_processor.save_data(typing_to_data)
        if not process_result.success:
            raise ProfileCustomDataError(process_result.error or "Failed to process profile data")

        try:
            if user_uuid:
                query = SqlQuery[ProfileCustomFields]()
                query.add_filter(ProfileCustomFields.USER_UUID, user_uuid)
                existing = await self.repository.get(query)
                if existing:
                    raise ProfileCustomAlreadyExistsError(f"Profile already exists for user {user_uuid}")

            entity = ProfileCustomEntity(
                uuid=profile_uuid or str(uuid4()),
                data=process_result.processed_data,
                user_uuid=user_uuid,
            )

            created = await self.repository.save(entity)
            if not created:
                raise ProfileCustomDataError("Failed to save profile")

            return created

        except Exception:
            await self.data_processor.delete_data(process_result.processed_data)
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
        typing_to_data: List[Tuple[str, Any]],
    ) -> ProfileCustomEntity:
        entity = await self.get(user_uuid=user_uuid)
        if not entity:
            raise ProfileCustomNotFoundError(f"Profile for user {user_uuid} not found")

        process_result = await self.data_processor.update_data(
            old_data=entity.data,
            new_typing_to_data=typing_to_data,
        )
        if not process_result.success:
            raise ProfileCustomDataError(process_result.error or "Failed to process profile data")

        entity.data = process_result.processed_data

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

        if entity.data:
            await self.data_processor.delete_data(entity.data)

        return True


def get_profile_custom_service() -> ProfileCustomService:
    return ProfileCustomService()
