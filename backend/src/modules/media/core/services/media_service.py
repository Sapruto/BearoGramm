from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
import hashlib

from sqlalchemy.exc import IntegrityError

from src.core.logger import get_logger
from src.core.settings import Settings
from src.general.repository.sql.sql_query import SqlQuery

from ..validators.media_validator import MediaValidator, get_default_media_validator
from ..storages.storage_api import StorageAPI, get_storage_api
from ..exceptions import NotFoundError, StorageError

from ..repositories.media_repository import (
    MediaRepository,
    get_media_repository,
)
from ...models.dto import (
    MediaDTO,
    UploadMediaResponse,
    DeleteMediaResponse,
    MediaExistsResponse,
)
from ...models.enums import MediaType
from ...models.media_entity import MediaEntity, MediaFields

logger = get_logger(__name__)


class MediaService:
    def __init__(
        self,
        storage: Optional[StorageAPI] = None,
        validator: Optional[MediaValidator] = None,
        repository: Optional[MediaRepository] = None,
    ):
        self._storage = storage or get_storage_api()
        self._validator = validator or get_default_media_validator()
        self._repository = repository or get_media_repository()

    @staticmethod
    def _make_media_uuid() -> str:
        return str(uuid4())

    @staticmethod
    def _storage_key_from_url(url: str) -> str:
        return url.rsplit("/", 1)[-1]

    @staticmethod
    def _compute_hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def _make_full_url(self, url: str):
        return Settings.MEDIA_BASE_URL + "/" + url

    async def _get_or_raise(self, media_id: str) -> MediaEntity:
        entity = await self._repository.get(media_id)
        if not entity:
            raise NotFoundError(f"Media not found: {media_id}")
        return entity

    def _to_dto(self, entity: MediaEntity) -> MediaDTO:
        return MediaDTO(
            uuid=entity.uuid,
            filename=entity.filename,
            url=entity.full_url,
            content_type=entity.content_type,
            size=entity.size,
            uploaded_at=entity.created_at,
            castrated_url=entity.url
        )

    async def upload_media(
            self,
            content: bytes,
            filename: str,
            media_type: MediaType,
            content_type: str,
    ) -> UploadMediaResponse:
        is_valid, err = self._validator.validate(content, content_type, media_type)
        if not is_valid:
            logger.warning(f"Media validation failed: {err}")
            return UploadMediaResponse(success=False, error=err)

        media_hash = self._compute_hash(content)

        existing = await self._repository.get(SqlQuery[MediaFields]().add_filter(MediaFields.HASH, media_hash))
        if existing:
            return UploadMediaResponse(success=True, media=self._to_dto(existing))

        ok, url = await self._storage.upload_file(
            file_content=content,
            filename=filename,
            content_type=content_type,
        )
        if not ok or not url:
            logger.error(f"Media upload failed: {url}")
            return UploadMediaResponse(
                success=False, error=url or "Upload failed"
            )

        entity = MediaEntity(
            uuid=self._make_media_uuid(),
            full_url=self._make_full_url(url),
            url=url,
            hash=media_hash,
            filename=filename,
            content_type=content_type or "application/octet-stream",
            media_type=media_type,
            size=len(content),
            version=1,
            created_at=datetime.now(timezone.utc),
        )

        try:
            saved = await self._repository.save(entity)
        except IntegrityError:
            logger.warning(f"Race on hash={media_hash}, falling back to existing")
            try:
                await self._storage.unload_file(self._storage_key_from_url(url))
            except Exception as rollback_err:
                logger.error(f"Rollback storage unload failed: {rollback_err}")
            existing = await self._repository.get_by_hash(media_hash)
            # if existing:
            #     return UploadMediaResponse(success=True, media=self._to_dto(existing))
            return UploadMediaResponse(success=False, error="Persistence race failed")
        except Exception as e:
            logger.error(f"Failed to persist media: {e}")
            try:
                await self._storage.unload_file(self._storage_key_from_url(url))
            except Exception as rollback_err:
                logger.error(f"Rollback storage unload failed: {rollback_err}")
            return UploadMediaResponse(success=False, error="Persistence failed")

        return UploadMediaResponse(success=True, media=self._to_dto(saved))

    async def unload_media(self, media_uuid: str) -> DeleteMediaResponse:
        entity = await self._get_or_raise(media_uuid)

        storage_key = self._storage_key_from_url(entity.url)

        try:
            ok = await self._storage.unload_file(storage_key)
        except Exception as e:
            logger.error(f"Storage unload error: {e}")
            raise StorageError(str(e))

        if not ok:
            return DeleteMediaResponse(
                success=False, filename=entity.url, error="Storage delete failed"
            )

        await self._repository.delete(media_uuid)
        return DeleteMediaResponse(success=True, filename=entity.url)

    async def media_exists(self, media_id: str) -> MediaExistsResponse:
        entity = await self._repository.get(media_id)
        if not entity:
            return MediaExistsResponse(exists=False, filename=media_id)

        storage_key = self._storage_key_from_url(entity.url)
        exists = await self._storage.storage_impl.file_exists(storage_key)
        return MediaExistsResponse(exists=exists, filename=entity.url)

    async def get_media(self, media_id: str) -> MediaDTO:
        entity = await self._get_or_raise(media_id)
        return self._to_dto(entity)

    async def verify_avatar_url(self, avatar_url: str) -> bool:
        media = self._repository.get(SqlQuery[MediaFields](value=avatar_url, field=MediaFields.URL))
        if not media:
            return False
        return media.media_type == MediaType.IMAGE


def get_media_service() -> MediaService:
    return MediaService()
[]