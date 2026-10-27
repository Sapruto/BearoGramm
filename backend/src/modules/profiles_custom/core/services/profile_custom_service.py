from typing import Optional, Dict, List
from datetime import datetime, timezone

from src.core.logger import get_logger
from src.general.repository.sql.sql_query import SqlQuery
from src.modules.media.core.services.media_service import get_media_service, MediaService
from src.modules.user import get_user_service_api, UserServiceAPI

from ..exceptions import (
    ProfileCustomNotFoundError,
    ProfileCustomDataError,
    ProfileCustomAlreadyExistsError, BadAvatarUrl, NotFoundProfile,
)
from ...models.dto.profile_custom_requests import UpdateProfileRequest
from ...models.dto.profile_custom_responses import GetProfileResponse
from ...models.entities.profile_custom_entity import (
    ProfileCustomEntity,
    ProfileCustomFields,
)
from ..repositories.profile_custom_repository import get_profile_custom_repository, ProfileCustomRepository

logger = get_logger(__name__)


class ProfileCustomService:
    def __init__(self, repository: Optional[ProfileCustomRepository] = None, media_service: Optional[MediaService] = None, user_service: Optional[UserServiceAPI] = None):
        self._repository = repository or get_profile_custom_repository()
        self._media_service = media_service or get_media_service()
        self._user_service = user_service or get_user_service_api()

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

        created = await self._repository.save(entity)
        if not created:
            raise ProfileCustomDataError("Failed to save profile")

        return created

    async def update_by_user(
        self,
        user_uuid: str,
        request: UpdateProfileRequest
    ) -> ProfileCustomEntity:
        if request.avatar_url is not None and not await self._media_service.verify_avatar_url(request.avatar_url):
            raise BadAvatarUrl()

        entity = await self.get(user_uuid=user_uuid)
        if not entity:
            raise ProfileCustomNotFoundError(f"Profile for user {user_uuid} not found")

        if request.name is not None:
            entity.name = request.name
        if request.avatar_url is not None:
            entity.avatar_url = request.avatar_url
        if request.banner_color is not None:
            entity.banner_color = request.banner_color
        if request.gender is not None:
            entity.gender = request.gender
        if request.bio is not None:
            entity.bio = request.bio
        entity.updated_at = datetime.now(timezone.utc)

        result = True
        if request.email or request.username:
            result = await self._user_service.update(user_uuid=user_uuid, email=request.email, username=request.username)

        updated = await self._repository.save(entity, to_update=True)
        if not updated or not result:
            raise ProfileCustomDataError("Failed to update profile")

        return updated

    async def delete_by_user(self, user_uuid: str) -> bool:
        entity = await self.get(user_uuid=user_uuid)
        if not entity:
            raise ProfileCustomNotFoundError(f"Profile for user {user_uuid} not found")

        query = SqlQuery[ProfileCustomFields]()
        query.add_filter(ProfileCustomFields.UUID, entity.uuid)
        deleted = await self._repository.delete(query)

        if not deleted:
            raise ProfileCustomDataError("Failed to delete profile")

        return True

    async def get_me_profile_response(
            self,
            profile_uuid: Optional[str] = None,
            user_uuid: Optional[str] = None,
    ) -> GetProfileResponse:
        query = SqlQuery[ProfileCustomFields]()
        if profile_uuid:
            query.add_filter(ProfileCustomFields.UUID, profile_uuid)
        if user_uuid:
            query.add_filter(field=ProfileCustomFields.USER_UUID, value=user_uuid)

        entity = await self._repository.get(query)
        user = await self._user_service.get_user_by_uuid(entity.user_uuid)

        if not entity or not user:
            raise NotFoundProfile()

        return GetProfileResponse(entity=entity, username=user.username, email=user.email)

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

        entity = await self._repository.get(query)
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
    
        profiles = await self._repository.get_by_user_uuids(user_uuids)
    
        result: Dict[str, ProfileCustomEntity] = {}
        for profile in profiles:
            if profile and profile.user_uuid:
                result[profile.user_uuid] = profile
        return result


def get_profile_custom_service() -> ProfileCustomService:
    return ProfileCustomService()
