from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from src.core.logger import get_logger
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
    MediaUploadResponse,
    MediaDeleteResponse,
    MediaExistsResponse,
)
from ...models.media_entity import MediaEntity, MediaFields

logger = get_logger(__name__)


class MediaService:
    def __init__(
        self,
        storage: Optional[StorageAPI] = None,
        validator: Optional[MediaValidator] = None,
        repository: Optional[MediaRepository] = None,
    ):
        self.storage = storage or get_storage_api()
        self.validator = validator or get_default_media_validator()
        self.repository = repository or get_media_repository()

    @staticmethod
    def _make_media_uuid() -> str:
        return str(uuid4())

    @staticmethod
    def _storage_key_from_url(url: str) -> str:
        return url.rsplit("/", 1)[-1]

    @staticmethod
    def _compute_hash(content: bytes) -> str:
        import hashlib
        return hashlib.sha256(content).hexdigest()

    async def _get_or_raise(self, media_id: str) -> MediaEntity:
        entity = await self.repository.get(media_id)
        if not entity:
            raise NotFoundError(f"Media not found: {media_id}")
        return entity

    def _to_dto(self, entity: MediaEntity) -> MediaDTO:
        return MediaDTO(
            uuid=entity.uuid,
            filename=entity.filename,
            url=entity.url,
            content_type=entity.content_type,
            size=entity.size,
            uploaded_at=entity.created_at,
        )

    async def upload_media(
            self,
            content: bytes,
            filename: str,
            content_type: Optional[str] = None,
    ) -> MediaUploadResponse:
        is_valid, err = self.validator.validate(content, filename)
        if not is_valid:
            logger.warning(f"Media validation failed: {err}")
            return MediaUploadResponse(success=False, error=err)

        media_hash = self._compute_hash(content)

        existing = await self.repository.get(SqlQuery[MediaFields]().add_filter(MediaFields.HASH, media_hash))
        if existing:
            return MediaUploadResponse(success=True, media=self._to_dto(existing))

        ok, url_or_err = await self.storage.upload_file(
            file_content=content,
            filename=filename,
            content_type=content_type,
        )
        if not ok or not url_or_err:
            logger.error(f"Media upload failed: {url_or_err}")
            return MediaUploadResponse(
                success=False, error=url_or_err or "Upload failed"
            )

        url = url_or_err

        entity = MediaEntity(
            uuid=self._make_media_uuid(),
            url=url,
            hash=media_hash,
            filename=filename,
            content_type=content_type or "application/octet-stream",
            size=len(content),
            version=1,
            created_at=datetime.now(timezone.utc),
        )

        try:
            saved = await self.repository.save(entity)
        except IntegrityError:
            logger.warning(f"Race on hash={media_hash}, falling back to existing")
            try:
                await self.storage.unload_file(self._storage_key_from_url(url))
            except Exception as rollback_err:
                logger.error(f"Rollback storage unload failed: {rollback_err}")
            existing = await self.repository.get_by_hash(media_hash)
            if existing:
                return MediaUploadResponse(success=True, media=self._to_dto(existing))
            return MediaUploadResponse(success=False, error="Persistence race failed")
        except Exception as e:
            logger.error(f"Failed to persist media: {e}")
            try:
                await self.storage.unload_file(self._storage_key_from_url(url))
            except Exception as rollback_err:
                logger.error(f"Rollback storage unload failed: {rollback_err}")
            return MediaUploadResponse(success=False, error="Persistence failed")

        return MediaUploadResponse(success=True, media=self._to_dto(saved))

    async def unload_media(self, media_uuid: str) -> MediaDeleteResponse:
        entity = await self._get_or_raise(media_uuid)

        storage_key = self._storage_key_from_url(entity.url)

        try:
            ok = await self.storage.unload_file(storage_key)
        except Exception as e:
            logger.error(f"Storage unload error: {e}")
            raise StorageError(str(e))

        if not ok:
            return MediaDeleteResponse(
                success=False, filename=entity.url, error="Storage delete failed"
            )

        await self.repository.delete(media_uuid)
        return MediaDeleteResponse(success=True, filename=entity.url)

    async def media_exists(self, media_id: str) -> MediaExistsResponse:
        entity = await self.repository.get(media_id)
        if not entity:
            return MediaExistsResponse(exists=False, filename=media_id)

        storage_key = self._storage_key_from_url(entity.url)
        exists = await self.storage.storage_impl.file_exists(storage_key)
        return MediaExistsResponse(exists=exists, filename=entity.url)

    async def get_media(self, media_id: str) -> MediaDTO:
        entity = await self._get_or_raise(media_id)
        return self._to_dto(entity)


def get_media_service() -> MediaService:
    return MediaService()
