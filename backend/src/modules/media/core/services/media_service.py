from datetime import datetime, timezone
from typing import Dict, List, Optional

from ..validators.media_validator import MediaValidator, get_default_media_validator
from ..storages.storage_api import StorageAPI, get_storage_api

from src.core.logger import get_logger

from ...models.dto import (
    MediaDTO,
    MediaMeta,
    MediaUploadResponse,
    MediaDeleteResponse,
    MediaExistsResponse,
)
from ..exceptions import NotFoundError, StorageError

logger = get_logger(__name__)


class MediaService:
    def __init__(
        self,
        storage: Optional[StorageAPI] = None,
        validator: Optional[MediaValidator] = None,
    ):
        self.storage = storage or get_storage_api()
        self.validator = validator or get_default_media_validator()
        self._registry: Dict[str, MediaMeta] = {}

    @staticmethod
    def _make_media_id() -> str:
        return f"att_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

    def _to_dto(self, meta: MediaMeta) -> MediaDTO:
        return MediaDTO(
            uuid=meta.uuid,
            filename=meta.filename,
            url=meta.url,
            content_type=meta.content_type,
            size=meta.size,
            uploaded_at=meta.uploaded_at,
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

        storage_key = url.rsplit("/", 1)[-1]

        meta = MediaMeta(
            id=self._make_media_id(),
            filename=filename,
            storage_key=storage_key,
            url=url,
            content_type=content_type or self.validator.get_file_extension(filename),
            size=len(content),
            uploaded_at=datetime.now(timezone.utc),
        )
        self._registry[meta.id] = meta

        logger.info(f"Media uploaded: id={meta.id}, url={url}")
        return MediaUploadResponse(success=True, media=self._to_dto(meta))

    async def unload_media(self, media_id: str) -> MediaDeleteResponse:
        meta = self._registry.get(media_id)
        if not meta:
            raise NotFoundError(f"Media not found: {media_id}")

        try:
            ok = await self.storage.unload_file(meta.storage_key)
        except Exception as e:
            logger.error(f"Storage unload error: {e}")
            raise StorageError(str(e))

        if not ok:
            return MediaDeleteResponse(
                success=False, filename=meta.filename, error="Storage delete failed"
            )

        self._registry.pop(media_id, None)
        logger.info(f"Media unloaded: id={media_id}")
        return MediaDeleteResponse(success=True, filename=meta.filename)

    async def media_exists(self, media_id: str) -> MediaExistsResponse:
        meta = self._registry.get(media_id)
        if not meta:
            return MediaExistsResponse(exists=False, filename=media_id)

        exists = await self.storage.storage_impl.file_exists(meta.storage_key)
        return MediaExistsResponse(exists=exists, filename=meta.filename)

    def get_media(self, media_id: str) -> MediaDTO:
        meta = self._registry.get(media_id)
        if not meta:
            raise NotFoundError(f"Media not found: {media_id}")
        return self._to_dto(meta)


_media_service_singleton: Optional[MediaService] = None


def get_media_service() -> MediaService:
    global _media_service_singleton
    if _media_service_singleton is None:
        _media_service_singleton = MediaService()
    return _media_service_singleton
