from pydantic import BaseModel, Field, field_validator


class SendCodeRequest(BaseModel):
    phone_number: str = Field()

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Phone number cannot be empty")
        if not v.startswith("+"):
            raise ValueError("Phone number must start with +")
        if len(v) < 10:
            raise ValueError("Phone number is too short")
        return v


class VerifyCodeRequest(BaseModel):
    phone_number: str = Field(
        description="Номер телефона в международном формате", examples=["+79001234567"]
    )
    code: str = Field(
        description="Код из SMS", min_length=5, max_length=5, examples=["12345"]
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Phone number cannot be empty")
        if not v.startswith("+"):
            raise ValueError("Phone number must start with +")
        if len(v) < 10:
            raise ValueError("Phone number is too short")
        return v

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Code cannot be empty")
        if not v.isdigit():
            raise ValueError("Code must contain only digits")
        if len(v) != 5:
            raise ValueError("Code must be exactly 5 digits")
        return v
