from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request

from src.core.limiter import limiter
from src.modules.profiles_custom.core.services.profile_custom_service import get_profile_custom_service
from .auth_route_names import AuthRoutes
from ...core.services.auth_service import get_auth_service
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
from ...core.use_cases import AuthUseCases
from ...models.dto.requests import SendCodeRequest, VerifyCodeRequest
from ...models.dto.responses import SendCodeResponse, VerifyCodeResponse


auth_router = APIRouter(prefix=AuthRoutes.base, tags=["auth"])


def get_use_cases() -> AuthUseCases:
    return AuthUseCases(get_auth_service(), get_profile_custom_service())


@auth_router.post(
    AuthRoutes.send_code,
    response_model=SendCodeResponse,
    status_code=status.HTTP_200_OK
)
@limiter.limit("10/10minutes")
async def send_code(
    request: Request,
    data: SendCodeRequest,
    use_cases: AuthUseCases = Depends(get_use_cases)
) -> SendCodeResponse:
    try:
        return await use_cases.send_code(data)
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
@limiter.limit("10/10minutes")
async def verify_code(
    request: Request,
    data: VerifyCodeRequest,
    use_cases: AuthUseCases = Depends(get_use_cases)
) -> VerifyCodeResponse:
    try:
        return await use_cases.verify_phone(data)
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
