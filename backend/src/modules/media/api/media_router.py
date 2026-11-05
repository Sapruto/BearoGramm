from fastapi import APIRouter, Depends, HTTPException, status

from ..models.dto import (
    MediaDTO,
    MediaExistsResponse,
)
from ..core.exceptions import NotFoundError
from ..core.services.media_service import MediaService, get_media_service


media_router = APIRouter(prefix="/api/medias", tags=["medias"])


@media_router.get(
    "/{media_uuid}",
    response_model=MediaDTO,
)
async def get_media(
    media_uuid: str,
    service: MediaService = Depends(get_media_service),
) -> MediaDTO:
    try:
        return await service.get_media(media_uuid)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@media_router.get(
    "/{media_uuid}/exists",
    response_model=MediaExistsResponse,
)
async def media_exists(
    media_uuid: str,
    service: MediaService = Depends(get_media_service),
) -> MediaExistsResponse:
    return await service.media_exists(media_uuid)
