import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from src.modules.user.models.entities.user_entity import UserEntity, UserFields


@pytest.mark.unit
class TestUserEntity:
    def test_user_entity_creation(self):
        user_uuid = str(uuid4())
        now = datetime.now()

        user = UserEntity(
            uuid=user_uuid, phone_number="+79001234567", created_at=now, updated_at=now
        )

        assert user.uuid == user_uuid
        assert user.phone_number == "+79001234567"
        assert user.created_at == now
        assert user.updated_at == now

    def test_user_entity_required_fields(self):
        with pytest.raises(ValidationError):
            UserEntity()

    def test_user_entity_optional_fields(self):
        user = UserEntity(phone_number="+79001234567")
        assert user.uuid is None
        assert user.created_at is None
        assert user.updated_at is None

    def test_user_fields_enum(self):
        assert UserFields.UUID == "uuid"
        assert UserFields.PHONE_NUMBER == "phone_number"
        assert UserFields.PHONE_NUMBER_HASH == "phone_number_hash"
        assert UserFields.PHONE_NUMBER_MASK == "phone_number_mask"
        assert UserFields.CREATED_AT == "created_at"
        assert UserFields.UPDATED_AT == "updated_at"

    def test_user_fields_str(self):
        field = UserFields.UUID
        assert str(field) == "uuid"
