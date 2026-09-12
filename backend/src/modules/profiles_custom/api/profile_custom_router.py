from fastapi import APIRouter, Depends, HTTPException, status

from src.core.logger import get_logger
from src.modules.user import get_current_user_depends

from ..core.exceptions import (
    ProfileCustomNotFoundError,
    ProfileCustomDataError,
    ProfileCustomAlreadyExistsError,
)
from ..core.services.profile_custom_service import (
    ProfileCustomService,
    get_profile_custom_service,
)
from ..models.dto.profile_custom_requests import (
    CreateProfileRequest,
    UpdateProfileRequest,
)
from ..models.dto.profile_custom_responses import (
    CreateProfileResponse,
    GetProfileResponse,
    UpdateProfileResponse,
    DeleteProfileResponse,
)

logger = get_logger(__name__)

profile_custom_router = APIRouter(
    prefix="/api/profile-custom", tags=["profile_custom"]
)


@profile_custom_router.get("/get_my_profile", response_model=GetProfileResponse)
async def get_my_profile(
    current_user=Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service),
) -> GetProfileResponse:
    try:
        profile = await service.get(user_uuid=current_user.uuid)
        if not profile:
            return GetProfileResponse(success=False)
        return GetProfileResponse(success=True, profile=profile)
    except Exception:
        logger.exception("Failed to get my profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile",
        )


@profile_custom_router.post(
    "/create_profile",
    response_model=CreateProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    request: CreateProfileRequest,
    current_user=Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service),
) -> CreateProfileResponse:
    try:
        profile = await service.create(
            typing_to_data=request.typing_to_data,
            user_uuid=current_user.uuid,
            name=request.name,
            avatar_url=request.avatar_url,
        )
        return CreateProfileResponse(
            success=True,
            message="Profile created successfully",
            profile=profile,
        )
    except ProfileCustomAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ProfileCustomDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        logger.exception("Failed to create profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create profile",
        )


@profile_custom_router.put("/update_profile", response_model=UpdateProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user=Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service),
) -> UpdateProfileResponse:
    try:
        profile = await service.update_by_user(
            user_uuid=current_user.uuid,
            typing_to_data=request.typing_to_data,
            name=request.name,
            avatar_url=request.avatar_url,
        )
        return UpdateProfileResponse(
            success=True,
            message="Profile updated successfully",
            profile=profile,
        )
    except ProfileCustomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProfileCustomDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        logger.exception("Failed to update profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )


@profile_custom_router.delete(
    "/delete_profile", response_model=DeleteProfileResponse
)
async def delete_profile(
    current_user=Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service),
) -> DeleteProfileResponse:
    try:
        await service.delete_by_user(current_user.uuid)
        return DeleteProfileResponse(
            success=True, message="Profile deleted successfully"
        )
    except ProfileCustomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.exception("Failed to delete profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete profile",
        )


@profile_custom_router.get("/{profile_uuid}", response_model=GetProfileResponse)
async def get_profile(
    profile_uuid: str,
    current_user=Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service),
) -> GetProfileResponse:
    try:
        profile = await service.get(profile_uuid=profile_uuid)
        if not profile:
            return GetProfileResponse(success=False)
        return GetProfileResponse(success=True, profile=profile)
    except Exception:
        logger.exception("Failed to get profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile",
        )


@profile_custom_router.get(
    "/user/{user_uuid}", response_model=GetProfileResponse
)
async def get_profile_by_user(
    user_uuid: str,
    current_user=Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service),
) -> GetProfileResponse:
    try:
        profile = await service.get(user_uuid=user_uuid)
        if not profile:
            return GetProfileResponse(success=False)
        return GetProfileResponse(success=True, profile=profile)
    except Exception:
        logger.exception("Failed to get profile by user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile",
        )
