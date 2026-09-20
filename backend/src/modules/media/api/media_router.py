from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from ..models.dto import (
    MediaDTO,
    MediaDeleteResponse,
    MediaExistsResponse,
    MediaUploadResponse,
)
from ..core.exceptions import NotFoundError, StorageError
from ..core.services.media_service import MediaService, get_media_service

media_router = APIRouter(prefix="/api/medias", tags=["medias"])


@media_router.post(
    "/upload",
    response_model=MediaUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_media(
    file: UploadFile = File(...),
    content_type: Optional[str] = Form(default=None),
    service: MediaService = Depends(get_media_service),
) -> MediaUploadResponse:
    content = await file.read()
    result = await service.upload_media(
        content=content,
        filename=file.filename or "file",
        content_type=content_type or file.content_type,
    )
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error or "Upload failed",
        )
    return result


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
