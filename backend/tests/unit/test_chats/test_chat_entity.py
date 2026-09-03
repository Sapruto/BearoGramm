import pytest
from datetime import datetime, timezone

from src.modules.chats.models.entities.chat_entity import ChatEntity, ChatFields


@pytest.mark.unit
class TestChatEntity:
    def test_chat_entity_creation(
        self, sample_chat_uuid, sample_user_uuid, sample_companion_uuid
    ):
        now = datetime.now(timezone.utc)
        access1 = PersonalAccessType(user_uuid=sample_user_uuid)
        access2 = PersonalAccessType(user_uuid=sample_companion_uuid)

        chat = ChatEntity(
            uuid=sample_chat_uuid,
            accesses=[access1, access2],
            created_at=now,
            updated_at=now,
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

    def test_chat_entity_empty_accesses_allowed(self):
        chat = ChatEntity(accesses=[])
        assert chat.accesses == []

    def test_chat_fields_enum(self):
        assert ChatFields.UUID == "uuid"
        assert ChatFields.ACCESSES == "accesses"
        assert ChatFields.CREATED_AT == "created_at"
        assert ChatFields.UPDATED_AT == "updated_at"
        assert ChatFields.CHAT_TYPE == "chat_type"
