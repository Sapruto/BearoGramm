from typing import Optional, Dict, Any, List, Tuple
from uuid import uuid4
from datetime import datetime, timezone

from src.core.logger import get_logger
from src.general.processors.data_processor import DataProcessor
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
        self.data_processor = DataProcessor()

    async def create(
        self,
        typing_to_data: List[Tuple[str, Any]],
        user_uuid: Optional[str] = None,
        profile_uuid: Optional[str] = None,
        name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> ProfileCustomEntity:
        if user_uuid:
            existing = await self.get(user_uuid=user_uuid)
            if existing:
                raise ProfileCustomAlreadyExistsError(
                    f"Profile already exists for user {user_uuid}"
                )

        result = await self.data_processor.save_data(typing_to_data)
        if not result.success:
            raise ProfileCustomDataError(result.error or "Failed to process data")

        entity = ProfileCustomEntity(
            uuid=profile_uuid or str(uuid4()),
            name=name or "Unified",
            avatar_url=avatar_url or ProfileCustomEntity.model_fields["avatar_url"].default,
            data=result.processed_data,
            user_uuid=user_uuid,
            updated_at=datetime.now(timezone.utc),
        )

        created = await self.repository.save(entity)
        if not created:
            await self.data_processor.delete_data(result.processed_data)
            raise ProfileCustomDataError("Failed to save profile")

        return created

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
        print(entity)
        return entity

    async def _prepare_data_to_use(self, data: List[Any]) -> List[Any]:
        if not data:
            return []
        return await self.repository.mapper.prepare_data_to_use(data)

    async def update_by_user(
        self,
        user_uuid: str,
        typing_to_data: List[Tuple[str, Any]],
        name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> ProfileCustomEntity:
        entity = await self.get(user_uuid=user_uuid)
        if not entity:
            raise ProfileCustomNotFoundError(f"Profile for user {user_uuid} not found")

        result = await self.data_processor.update_data(
            old_data=entity.data,
            new_typing_to_data=typing_to_data,
        )
        if not result.success:
            raise ProfileCustomDataError(result.error or "Failed to update data")

        entity.data = result.processed_data
        if name is not None:
            entity.name = name
        if avatar_url is not None:
            entity.avatar_url = avatar_url
        entity.updated_at = datetime.now(timezone.utc)

        updated = await self.repository.update(entity)
        if not updated:
            raise ProfileCustomDataError("Failed to update profile")

        return updated

    async def delete_by_user(self, user_uuid: str) -> bool:
        entity = await self.get(user_uuid=user_uuid)
        if not entity:
            raise ProfileCustomNotFoundError(f"Profile for user {user_uuid} not found")

        await self.data_processor.delete_data(entity.data)

        query = SqlQuery[ProfileCustomFields]()
        query.add_filter(ProfileCustomFields.UUID, entity.uuid)
        deleted = await self.repository.delete(query)

        if not deleted:
            raise ProfileCustomDataError("Failed to delete profile")

        return True

    async def get_by_user_uuid(
        self, user_uuid: str
    ) -> Optional[ProfileCustomEntity]:
        return await self.get(user_uuid=user_uuid)

    async def get_by_user_uuids(
        self, user_uuids: List[str]
    ) -> Dict[str, ProfileCustomEntity]:
        profiles = await self.repository.get_by_user_uuids(user_uuids)

        result: Dict[str, ProfileCustomEntity] = {}
        for profile in profiles:
            if profile.user_uuid:
                profile.data = await self._prepare_data_to_use(profile.data)
                result[profile.user_uuid] = profile
        return result


def get_profile_custom_service() -> ProfileCustomService:
    return ProfileCustomService()
