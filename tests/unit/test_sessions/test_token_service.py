import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import jwt

from src.modules.sessions.core.services.token_service import TokenService


@pytest.mark.unit
class TestTokenService:
    def test_create_access_token(self, token_service):
        data = {"user_uuid": "test_uuid"}
        token = token_service.create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expires(self, token_service):
        data = {"user_uuid": "test_uuid"}
        expires_delta = timedelta(hours=1)
        token = token_service.create_access_token(data, expires_delta)

        assert token is not None

    def test_verify_token_valid(self, token_service):
        data = {"user_uuid": "test_uuid", "session_id": "test_session"}
        token = token_service.create_access_token(data)

        payload = token_service.verify_token(token)

        assert payload is not None
        assert payload["user_uuid"] == "test_uuid"
        assert payload["session_id"] == "test_session"

    def test_verify_token_expired(self, token_service):
        with patch('src.modules.sessions.core.services.token_service.jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")

            payload = token_service.verify_token("expired_token")

            assert payload is None

    def test_verify_token_invalid(self, token_service):
        with patch('src.modules.sessions.core.services.token_service.jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")

            payload = token_service.verify_token("invalid_token")

            assert payload is None

    def test_decode_token(self, token_service):
        data = {"user_uuid": "test_uuid", "session_id": "test_session"}
        token = token_service.create_access_token(data)

        payload = token_service.decode_token(token)

        assert payload is not None
        assert payload["user_uuid"] == "test_uuid"

    def test_decode_token_invalid(self, token_service):
        with patch('src.modules.sessions.core.services.token_service.jwt.decode') as mock_decode:
            mock_decode.side_effect = Exception("Decode error")

            payload = token_service.decode_token("invalid_token")

            assert payload is None

    def test_get_token_service(self):
        from src.modules.sessions.core.services.token_service import get_token_service
        service = get_token_service()
        assert isinstance(service, TokenService)
