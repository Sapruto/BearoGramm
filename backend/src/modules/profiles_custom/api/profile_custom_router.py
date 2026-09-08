from typing import List, Tuple, Any
from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.user import get_current_user_depends

from ..core.exceptions import (
    ProfileCustomNotFoundError,
    ProfileCustomDataError,
    ProfileCustomAlreadyExistsError,
)
from ..core.services.profile_custom_service import ProfileCustomService, get_profile_custom_service
from ..models.entities.profile_custom_entity import ProfileCustomEntity


profile_custom_router = APIRouter(prefix="/api/profile-custom", tags=["profile_custom"])


@profile_custom_router.get(
    "/get_my_profile",
    response_model=ProfileCustomEntity,
    status_code=status.HTTP_200_OK
)
async def get_my_profile(
    current_user = Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service)
) -> ProfileCustomEntity:
    try:
        profile = await service.get(user_uuid=current_user.uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@profile_custom_router.post(
    "/create_profile",
    response_model=ProfileCustomEntity,
    status_code=status.HTTP_201_CREATED
)
async def create_profile(
    typing_to_data: List[Tuple[str, Any]],
    current_user = Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service)
) -> ProfileCustomEntity:
    try:
        return await service.create(
            typing_to_data=typing_to_data,
            user_uuid=current_user.uuid
        )
    except ProfileCustomAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ProfileCustomDataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}"
        )


@profile_custom_router.put(
    "/update_profile",
    response_model=ProfileCustomEntity,
    status_code=status.HTTP_200_OK
)
async def update_profile(
    typing_to_data: List[Tuple[str, Any]],
    current_user = Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service)
) -> ProfileCustomEntity:
    try:
        return await service.update_by_user(
            user_uuid=current_user.uuid,
            typing_to_data=typing_to_data
        )
    except ProfileCustomNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ProfileCustomDataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@profile_custom_router.delete(
    "/delete_profile",
    response_model=dict,
    status_code=status.HTTP_200_OK
)
async def delete_profile(
    current_user = Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service)
) -> dict:
    try:
        await service.delete_by_user(current_user.uuid)
        return {"message": "Profile deleted successfully"}
    except ProfileCustomNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile: {str(e)}"
        )


@profile_custom_router.get(
    "/{profile_uuid}",
    response_model=ProfileCustomEntity,
    status_code=status.HTTP_200_OK
)
async def get_profile(
    profile_uuid: str,
    current_user = Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service)
) -> ProfileCustomEntity:
    try:
        profile = await service.get(profile_uuid=profile_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile {profile_uuid} not found"
            )
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@profile_custom_router.get(
    "/user/{user_uuid}",
    response_model=ProfileCustomEntity,
    status_code=status.HTTP_200_OK
)
async def get_profile_by_user(
    user_uuid: str,
    current_user = Depends(get_current_user_depends()),
    service: ProfileCustomService = Depends(get_profile_custom_service)
) -> ProfileCustomEntity:
    try:
        profile = await service.get(user_uuid=current_user.user_uuid)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile for user {user_uuid} not found"
            )
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )
