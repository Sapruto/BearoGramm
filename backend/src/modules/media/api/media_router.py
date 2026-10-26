from fastapi import APIRouter, Request, Depends, File, Form, HTTPException, UploadFile, status

from ..models.dto import (
    MediaDTO,
    MediaExistsResponse,
    UploadMediaResponse,
)
from ..core.exceptions import NotFoundError
from ..core.services.media_service import MediaService, get_media_service
from ..models.enums import MediaType

from src.core.limiter import limiter

media_router = APIRouter(prefix="/api/medias", tags=["medias"])


@media_router.post(
    "/upload",
    response_model=UploadMediaResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/1minutes")
async def upload_media(
    request: Request,
    media_type: MediaType = Form(..., max_length=255),
    file: UploadFile = File(...),
    service: MediaService = Depends(get_media_service),
) -> UploadMediaResponse:
    content = await file.read()
    result = await service.upload_media(
        content=content,
        filename=file.filename or "file",
        content_type=file.content_type,
        media_type=media_type
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
