import pytest
from datetime import datetime
from uuid import uuid4

from src.modules.chats.chat_types.personal.models.personal_contact import (
    PersonalContact,
)


@pytest.mark.unit
class TestPersonalContact:
    def test_personal_contact_creation(self):
        chat_uuid = str(uuid4())
        user_uuid = str(uuid4())

        contact = PersonalContact(chat_uuid=chat_uuid, user_uuid=user_uuid)

        assert contact.chat_uuid == chat_uuid
        assert contact.user_uuid == user_uuid
        assert contact.is_blocked is False
        assert contact.unread_count == 0
        assert contact.last_message_at is None
        assert contact.created_at is None
        assert contact.updated_at is None

    def test_personal_contact_with_all_fields(self):
        chat_uuid = str(uuid4())
        user_uuid = str(uuid4())
        now = datetime.now()

        contact = PersonalContact(
            chat_uuid=chat_uuid,
            user_uuid=user_uuid,
            is_blocked=True,
            last_message_at=now,
            unread_count=5,
            created_at=now,
            updated_at=now,
        )

        assert contact.chat_uuid == chat_uuid
        assert contact.user_uuid == user_uuid
        assert contact.is_blocked is True
        assert contact.last_message_at == now
        assert contact.unread_count == 5
        assert contact.created_at == now
        assert contact.updated_at == now

    def test_personal_contact_defaults(self):
        contact = PersonalContact(chat_uuid=str(uuid4()), user_uuid=str(uuid4()))
        assert contact.is_blocked is False
        assert contact.unread_count == 0
        assert contact.last_message_at is None
        assert contact.created_at is None
        assert contact.updated_at is None

    def test_personal_contact_with_blocked_true(self):
        contact = PersonalContact(
            chat_uuid=str(uuid4()), user_uuid=str(uuid4()), is_blocked=True
        )
        assert contact.is_blocked is True

    def test_personal_contact_with_unread_count(self):
        contact = PersonalContact(
            chat_uuid=str(uuid4()), user_uuid=str(uuid4()), unread_count=99
        )
        assert contact.unread_count == 99

    def test_personal_contact_fields_types(self):
        contact = PersonalContact(chat_uuid=str(uuid4()), user_uuid=str(uuid4()))
        assert isinstance(contact.chat_uuid, str)
        assert isinstance(contact.user_uuid, str)
        assert isinstance(contact.is_blocked, bool)
        assert isinstance(contact.unread_count, int)
