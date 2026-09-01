import pytest
from fastapi import status

from src.modules.user.api.exceptions import (
    UserHaveNotAccess,
    UserNotFound,
    InvalidTokenError,
)


@pytest.mark.unit
class TestExceptions:
    def test_user_have_not_access(self):
        exc = UserHaveNotAccess()
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "User have no chat_types"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_user_have_not_access_custom_message(self):
        exc = UserHaveNotAccess("Custom message")
        assert exc.detail == "Custom message"

    def test_user_not_found(self):
        exc = UserNotFound()
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "User not found"

    def test_user_not_found_custom_message(self):
        exc = UserNotFound("User with id 1 not found")
        assert exc.detail == "User with id 1 not found"

    def test_invalid_token_error(self):
        exc = InvalidTokenError()
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.detail == "Invalid token"

    def test_invalid_token_error_custom_message(self):
        exc = InvalidTokenError("Token expired")
        assert exc.detail == "Token expired"
