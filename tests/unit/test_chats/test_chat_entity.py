import pytest
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import ValidationError

from src.modules.chats.models.entities.chat_entity import ChatEntity, ChatFields
from src.modules.chats.chat_types.personal.models.personal_access_type import PersonalAccessType, PERSONAL_TYPE


@pytest.mark.unit
class TestChatEntity:
    def test_chat_entity_creation(self, sample_chat_uuid, sample_user_uuid, sample_companion_uuid):
        now = datetime.now(timezone.utc)
        access1 = PersonalAccessType(user_uuid=sample_user_uuid)
        access2 = PersonalAccessType(user_uuid=sample_companion_uuid)

        chat = ChatEntity(
            uuid=sample_chat_uuid,
            accesses=[access1, access2],
            created_at=now,
            updated_at=now
        )

        assert chat.uuid == sample_chat_uuid
        assert len(chat.accesses) == 2
        assert chat.accesses[0].user_uuid == sample_user_uuid
        assert chat.accesses[1].user_uuid == sample_companion_uuid
        assert chat.created_at == now
        assert chat.updated_at == now

    def test_chat_entity_optional_fields(self, sample_user_uuid, sample_companion_uuid):
        access1 = PersonalAccessType(user_uuid=sample_user_uuid)
        access2 = PersonalAccessType(user_uuid=sample_companion_uuid)

        chat = ChatEntity(accesses=[access1, access2])

        assert chat.uuid is None
        assert chat.created_at is None
        assert chat.updated_at is None

    def test_chat_entity_min_accesses(self, sample_user_uuid):
        with pytest.raises(ValidationError):
            ChatEntity(accesses=[])

    def test_chat_entity_access_type_property(self, sample_user_uuid, sample_companion_uuid):
        access1 = PersonalAccessType(user_uuid=sample_user_uuid)
        access2 = PersonalAccessType(user_uuid=sample_companion_uuid)

        chat = ChatEntity(accesses=[access1, access2])
        assert chat.access_type == PERSONAL_TYPE

    def test_chat_entity_empty_access_type(self):
        with pytest.raises(ValidationError):
            ChatEntity(accesses=[])

    def test_chat_entity_add_access(self, sample_chat_uuid, sample_user_uuid, sample_companion_uuid):
        access1 = PersonalAccessType(user_uuid=sample_user_uuid)
        chat = ChatEntity(accesses=[access1])

        access2 = PersonalAccessType(user_uuid=sample_companion_uuid)
        chat.add_access(access2)

        assert len(chat.accesses) == 2
        assert chat.accesses[1].user_uuid == sample_companion_uuid

    def test_chat_entity_remove_access(self, sample_chat_uuid, sample_user_uuid, sample_companion_uuid):
        access1 = PersonalAccessType(user_uuid=sample_user_uuid)
        access2 = PersonalAccessType(user_uuid=sample_companion_uuid)

        chat = ChatEntity(accesses=[access1, access2])
        chat.remove_access(access1)

        assert len(chat.accesses) == 1
        assert chat.accesses[0].user_uuid == sample_companion_uuid

    def test_chat_entity_remove_access_not_exists(self, sample_chat_uuid, sample_user_uuid, sample_companion_uuid):
        access1 = PersonalAccessType(user_uuid=sample_user_uuid)
        access2 = PersonalAccessType(user_uuid=sample_companion_uuid)
        access3 = PersonalAccessType(user_uuid=str(uuid4()))

        chat = ChatEntity(accesses=[access1, access2])
        chat.remove_access(access3)

        assert len(chat.accesses) == 2

    def test_chat_fields_enum(self):
        assert ChatFields.UUID == "uuid"
        assert ChatFields.ACCESSES == "accesses"
        assert ChatFields.CREATED_AT == "created_at"
        assert ChatFields.UPDATED_AT == "updated_at"
