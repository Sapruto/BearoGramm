import pytest
from pydantic import ValidationError

from src.modules.user.models.dto.requests import SendCodeRequest, VerifyCodeRequest
from src.modules.user.models.dto.responses import SendCodeResponse, VerifyCodeResponse
from src.modules.user.models.entities.user_entity import UserEntity


@pytest.mark.unit
class TestSendCodeRequest:
    def test_valid_phone(self):
        request = SendCodeRequest(phone_number="+79001234567")
        assert request.phone_number == "+79001234567"

    def test_phone_with_spaces(self):
        request = SendCodeRequest(phone_number="  +79001234567  ")
        assert request.phone_number == "+79001234567"

    def test_phone_without_plus(self):
        with pytest.raises(ValidationError) as exc:
            SendCodeRequest(phone_number="79001234567")
        assert "must start with +" in str(exc.value)

    def test_phone_empty(self):
        with pytest.raises(ValidationError) as exc:
            SendCodeRequest(phone_number="")
        assert "cannot be empty" in str(exc.value)

    def test_phone_too_short(self):
        with pytest.raises(ValidationError) as exc:
            SendCodeRequest(phone_number="+123")
        assert "too short" in str(exc.value)


@pytest.mark.unit
class TestVerifyCodeRequest:
    def test_valid_request(self):
        request = VerifyCodeRequest(
            phone_number="+79001234567",
            code="12345"
        )
        assert request.phone_number == "+79001234567"
        assert request.code == "12345"

    def test_phone_validation(self):
        with pytest.raises(ValidationError) as exc:
            VerifyCodeRequest(
                phone_number="79001234567",
                code="12345"
            )
        assert "must start with +" in str(exc.value)

    def test_code_validation_too_short(self):
        with pytest.raises(ValidationError) as exc:
            VerifyCodeRequest(
                phone_number="+79001234567",
                code="1234"
            )
        assert "String should have at least 5 characters" in str(exc.value)

    def test_code_validation_too_long(self):
        with pytest.raises(ValidationError) as exc:
            VerifyCodeRequest(
                phone_number="+79001234567",
                code="123456"
            )
        assert "String should have at most 5 characters" in str(exc.value)

    def test_code_with_letters(self):
        with pytest.raises(ValidationError) as exc:
            VerifyCodeRequest(
                phone_number="+79001234567",
                code="abc12"
            )
        assert "only digits" in str(exc.value)

    def test_code_empty(self):
        with pytest.raises(ValidationError) as exc:
            VerifyCodeRequest(
                phone_number="+79001234567",
                code=""
            )
        assert "String should have at least 5 characters" in str(exc.value)


@pytest.mark.unit
class TestVerifyCodeResponse:
    def test_success_response(self):
        response = VerifyCodeResponse(
            success=True,
            token="test_token",
            user_uuid="test_uuid"
        )
        assert response.success is True
        assert response.token == "test_token"
        assert response.user_uuid == "test_uuid"
        assert response.error_message is None

    def test_failure_response(self):
        response = VerifyCodeResponse(
            success=False,
            error_message="Invalid code"
        )
        assert response.success is False
        assert response.token is None
        assert response.user_uuid is None
        assert response.error_message == "Invalid code"

    def test_success_without_token_raises(self):
        with pytest.raises(ValueError):
            VerifyCodeResponse(
                success=True,
                error_message=None
            )

    def test_success_with_error_message_raises(self):
        with pytest.raises(ValueError):
            VerifyCodeResponse(
                success=True,
                token="test_token",
                user_uuid="test_uuid",
                error_message="Should not have error"
            )
