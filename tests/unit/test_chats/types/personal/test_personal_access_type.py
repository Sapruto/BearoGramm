import pytest
from datetime import datetime
from uuid import uuid4

from src.modules.chats.chat_types.personal.models.personal_access_type import PersonalAccessType, PERSONAL_TYPE
from src.modules.chats.chat_types.personal.models.personal_access_threshold import PersonalAccessThreshold
from src.modules.chats.chat_types.base.base_access_type import BaseAccessType


@pytest.mark.unit
class TestPersonalAccessType:
    def test_personal_access_type_inheritance(self):
        access = PersonalAccessType(user_uuid=str(uuid4()))
        assert isinstance(access, BaseAccessType)

    def test_personal_access_type_creation(self):
        user_uuid = str(uuid4())
        access = PersonalAccessType(user_uuid=user_uuid)

        assert access.user_uuid == user_uuid
        assert access.is_blocked is False
        assert access.unread_count == 0
        assert access.blocked_at is None
        assert access.blocked_by is None
        assert access.last_message_at is None

    def test_personal_access_type_with_all_fields(self):
        user_uuid = str(uuid4())
        now = datetime.now()
        blocked_by = str(uuid4())

        access = PersonalAccessType(
            user_uuid=user_uuid,
            is_blocked=True,
            blocked_at=now,
            blocked_by=blocked_by,
            last_message_at=now,
            unread_count=10
        )

        assert access.is_blocked is True
        assert access.blocked_at == now
        assert access.blocked_by == blocked_by
        assert access.last_message_at == now
        assert access.unread_count == 10

    def test_get_threshold(self):
        user_uuid = str(uuid4())
        access = PersonalAccessType(user_uuid=user_uuid)
        threshold = access.get_threshold()

        assert isinstance(threshold, PersonalAccessThreshold)
        assert threshold.is_blocked == access.is_blocked
        assert threshold.blocked_at == access.blocked_at
        assert threshold.blocked_by == access.blocked_by
        assert threshold.last_message_at == access.last_message_at
        assert threshold.unread_count == access.unread_count

    def test_get_threshold_with_blocked(self):
        user_uuid = str(uuid4())
        now = datetime.now()
        blocked_by = str(uuid4())

        access = PersonalAccessType(
            user_uuid=user_uuid,
            is_blocked=True,
            blocked_at=now,
            blocked_by=blocked_by,
            last_message_at=now,
            unread_count=5
        )

        threshold = access.get_threshold()

        assert threshold.is_blocked is True
        assert threshold.blocked_at == now
        assert threshold.blocked_by == blocked_by
        assert threshold.last_message_at == now
        assert threshold.unread_count == 5

    def test_get_raw_data(self):
        user_uuid = str(uuid4())
        now = datetime.now()
        blocked_by = str(uuid4())

        access = PersonalAccessType(
            user_uuid=user_uuid,
            is_blocked=True,
            blocked_at=now,
            blocked_by=blocked_by,
            last_message_at=now,
            unread_count=3
        )

        raw_data = access.get_raw_data()

        assert raw_data["user_uuid"] == user_uuid
        assert raw_data["is_blocked"] is True
        assert raw_data["blocked_at"] == now.isoformat()
        assert raw_data["blocked_by"] == blocked_by
        assert raw_data["last_message_at"] == now.isoformat()
        assert raw_data["unread_count"] == 3

    def test_get_raw_data_with_none_dates(self):
        access = PersonalAccessType(user_uuid=str(uuid4()))
        raw_data = access.get_raw_data()

        assert raw_data["blocked_at"] is None
        assert raw_data["last_message_at"] is None

    def test_get_type(self):
        access = PersonalAccessType(user_uuid=str(uuid4()))
        assert access.get_type() == PERSONAL_TYPE
        assert access.get_type() == "personal"

    def test_personal_type_constant(self):
        assert PERSONAL_TYPE == "personal"

    def test_create_from_user_uuid(self):
        user_uuid = str(uuid4())
        access = PersonalAccessType.create_from_user_uuid(user_uuid)

        assert access.user_uuid == user_uuid
        assert access.is_blocked is False
        assert access.unread_count == 0
        assert access.blocked_at is None
        assert access.blocked_by is None
        assert access.last_message_at is None

    def test_create_from_user_uuid_returns_personal_access_type(self):
        user_uuid = str(uuid4())
        access = PersonalAccessType.create_from_user_uuid(user_uuid)
        assert isinstance(access, PersonalAccessType)

    def test_personal_access_type_fields_optional(self):
        access = PersonalAccessType(user_uuid=str(uuid4()))
        assert access.blocked_at is None
        assert access.blocked_by is None
        assert access.last_message_at is None
