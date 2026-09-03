from fastapi import APIRouter, Depends, HTTPException, status

from .auth_route_names import AuthRoutes
from ...core.services.user_service import UserService, get_user_service
from ...core.exceptions import (
    FailedToCreateUser,
    FailedToSendCode,
    FailedToGetLoginToken,
    InvalidOrExpiredCode,
    UserNotFound,
    VerificationFailed,
    SessionCreationFailed,
    InvalidPhoneNumber
)
from ...models.dto.requests import SendCodeRequest, VerifyCodeRequest
from ...models.dto.responses import SendCodeResponse, VerifyCodeResponse


auth_router = APIRouter(prefix=AuthRoutes.base, tags=["auth"])


@auth_router.post(
    AuthRoutes.send_code,
    response_model=SendCodeResponse,
    status_code=status.HTTP_200_OK
)
async def send_code(
    request: SendCodeRequest,
    service: UserService = Depends(get_user_service)
) -> SendCodeResponse:
    try:
        return await service.send_code_and_register_if_not(request)
    except InvalidPhoneNumber as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_PHONE_NUMBER",
                "message": e.message,
                "details": e.details
            }
        )
    except FailedToCreateUser as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "FAILED_TO_CREATE_USER",
                "message": e.message,
                "details": e.details
            }
        )
    except FailedToSendCode as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "FAILED_TO_SEND_CODE",
                "message": e.message,
                "details": e.details
            }
        )
    except FailedToGetLoginToken as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "FAILED_TO_GET_LOGIN_TOKEN",
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        )


@auth_router.post(
    AuthRoutes.verify_phone,
    response_model=VerifyCodeResponse,
    status_code=status.HTTP_200_OK
)
async def verify_code(
    request: VerifyCodeRequest,
    service: UserService = Depends(get_user_service)
) -> VerifyCodeResponse:
    try:
        return await service.verify_phone(request)
    except InvalidPhoneNumber as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_PHONE_NUMBER",
                "message": e.message,
                "details": e.details
            }
        )
    except InvalidOrExpiredCode as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_OR_EXPIRED_CODE",
                "message": e.message,
                "details": e.details
            }
        )
    except UserNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "USER_NOT_FOUND",
                "message": e.message,
                "details": e.details
            }
        )
    except SessionCreationFailed as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SESSION_CREATION_FAILED",
                "message": e.message,
                "details": e.details
            }
        )
    except VerificationFailed as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "VERIFICATION_FAILED",
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        )
