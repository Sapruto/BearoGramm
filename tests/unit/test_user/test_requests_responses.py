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
            code="123456"
        )
        assert request.phone_number == "+79001234567"
        assert request.code == "123456"

    def test_phone_validation(self):
        with pytest.raises(ValidationError) as exc:
            VerifyCodeRequest(
                phone_number="79001234567",
                code="123456"
            )
        assert "must start with +" in str(exc.value)

    def test_code_validation(self):
        with pytest.raises(ValidationError) as exc:
            VerifyCodeRequest(
                phone_number="+79001234567",
                code="12345"
            )
        assert "String should have at least 6 characters" in str(exc.value)

    def test_code_with_letters(self):
        with pytest.raises(ValidationError) as exc:
            VerifyCodeRequest(
                phone_number="+79001234567",
                code="abc123"
            )
        assert "only digits" in str(exc.value)

    def test_code_empty(self):
        with pytest.raises(ValidationError) as exc:
            VerifyCodeRequest(
                phone_number="+79001234567",
                code=""
            )
        assert "String should have at least 6 characters" in str(exc.value)
