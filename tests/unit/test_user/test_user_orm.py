import pytest
from datetime import datetime
from src.modules.user.models.orm.user_orm import UserORM


@pytest.mark.unit
class TestUserORM:
    def test_user_orm_creation(self, sample_user_orm):
        assert isinstance(sample_user_orm.uuid, str)
        assert len(sample_user_orm.uuid) > 0
        assert sample_user_orm.phone_number_encrypted == "encrypted_phone_data"
        assert sample_user_orm.phone_number_hash == "hash_of_phone"
        assert sample_user_orm.phone_number_mask == "+79***4567"
        assert isinstance(sample_user_orm.created_at, datetime)
        assert isinstance(sample_user_orm.updated_at, datetime)

    def test_user_orm_table_name(self):
        assert UserORM.__tablename__ == "users"
