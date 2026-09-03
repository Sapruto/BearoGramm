import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from uuid import uuid4
import hashlib

from src.modules.user.core.repositories.mappers.user_mapper import UserMapper
from src.modules.user.models.entities.user_entity import UserEntity, UserFields
from src.modules.user.models.orm.user_orm import UserORM
from src.general.repository.exception import NotConvertableValue


@pytest.mark.unit
class TestUserMapper:
    def test_normalize_phone(self, user_mapper):
        test_cases = [
            ("+79001234567", "+79001234567"),
            ("89001234567", "+79001234567"),
            ("9001234567", "+79001234567"),
            ("+79991234567", "+79991234567"),
            ("89991234567", "+79991234567"),
        ]
        for input_phone, expected in test_cases:
            result = user_mapper._normalize_phone(input_phone)
            assert result == expected

    def test_hash_phone(self, user_mapper):
        phone = "+79001234567"

        with patch(
            "src.modules.user.core.repositories.mappers.user_mapper.Settings"
        ) as mock_settings:
            mock_settings.PHONE.HASH_SALT = "test_salt"

            mapper = UserMapper()
            hashed = mapper._hash_phone(phone)

            expected = hashlib.sha256(
                f"test_salt:+79001234567".encode("utf-8")
            ).hexdigest()

            assert hashed == expected
            assert len(hashed) == 64

    def test_to_orm_without_phone(self, user_mapper):
        entity = UserEntity(phone_number="")
        orm = user_mapper.to_orm(entity)
        assert orm.phone_number_encrypted is None
        assert orm.phone_number_hash is None
        assert orm.phone_number_mask is None

    def test_to_entity(self, user_mapper, sample_user_orm):
        entity = user_mapper.to_entity(sample_user_orm)
        assert isinstance(entity, UserEntity)
        assert entity.uuid == sample_user_orm.uuid
        assert entity.phone_number == "+79001234567"
        assert entity.created_at == sample_user_orm.created_at
        assert entity.updated_at == sample_user_orm.updated_at

    def test_to_orm_value(self, user_mapper):
        field, value = user_mapper.to_orm_value(UserFields.PHONE_NUMBER, "+79001234567")
        assert field == UserORM.phone_number_hash
        assert isinstance(value, str)
        assert len(value) == 64

    def test_to_orm_value_invalid(self, user_mapper):
        with pytest.raises(NotConvertableValue):
            user_mapper.to_orm_value(UserFields.PHONE_NUMBER, 123)

    def test_to_entity_value(self, user_mapper):
        field, value = user_mapper.to_entity_value(
            UserORM.phone_number_encrypted, "encrypted_data"
        )
        assert field == UserFields.PHONE_NUMBER
        assert value == "+79001234567"

    def test_to_entity_value_none(self, user_mapper):
        field, value = user_mapper.to_entity_value(UserORM.phone_number_encrypted, None)
        assert field == UserFields.PHONE_NUMBER
        assert value is None

    def test_field_mapping_consistency(self, user_mapper):
        for field, orm_attr in user_mapper.field_mapping.items():
            assert isinstance(field, UserFields)
            assert hasattr(UserORM, str(orm_attr).split(".")[-1])

    def test_reverse_field_mapping_consistency(self, user_mapper):
        for orm_attr, field in user_mapper.reverse_field_mapping.items():
            assert isinstance(field, UserFields)
            assert hasattr(UserORM, str(orm_attr).split(".")[-1])

    def test_to_orm_field(self, user_mapper):
        orm_field = user_mapper.to_orm_field(UserFields.UUID)
        assert orm_field == UserORM.uuid

    def test_to_orm_field_invalid(self, user_mapper):
        with pytest.raises(ValueError):
            user_mapper.to_orm_field("invalid_field")

    def test_to_entity_field(self, user_mapper):
        entity_field = user_mapper.to_entity_field(UserORM.uuid)
        assert entity_field == UserFields.UUID

    def test_to_entity_field_invalid(self, user_mapper):
        with pytest.raises(ValueError):
            user_mapper.to_entity_field("invalid_field")

    def test_get_field_name(self, user_mapper):
        name = user_mapper.get_field_name(UserORM.uuid)
        assert name == "uuid"
        name = user_mapper.get_field_name(UserORM.phone_number_encrypted)
        assert name == "phone_number_encrypted"
