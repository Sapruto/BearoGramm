import pytest
from datetime import datetime, timezone
from uuid import uuid4

from src.modules.messages.models.entities.message_entity import (
    MessageEntity,
    MessageFields,
)
from src.modules.messages.types.text.text_message_data import TextMessageData


@pytest.mark.unit
class TestMessageEntity:
    def test_message_entity_creation(self, sample_text_data):
        user_uuid = str(uuid4())
        chat_uuid = str(uuid4())
        now = datetime.now(timezone.utc)

        entity = MessageEntity(
            uuid=str(uuid4()),
            message_data=[sample_text_data],
            chat_uuid=chat_uuid,
            user_uuid=user_uuid,
            created_at=now,
            updated_at=now,
        )

        assert entity.uuid is not None
        assert len(entity.message_data) == 1
        assert entity.message_data[0].text == "Hello world"
        assert entity.chat_uuid == chat_uuid
        assert entity.user_uuid == user_uuid

    def test_message_entity_optional_fields(self):
        entity = MessageEntity(chat_uuid=str(uuid4()), user_uuid=str(uuid4()))

        assert entity.uuid is None
        assert entity.message_data == []
        assert entity.created_at is None
        assert entity.updated_at is None

    def test_message_entity_add_content(self, sample_text_data):
        entity = MessageEntity(chat_uuid=str(uuid4()), user_uuid=str(uuid4()))

        entity.add_content(sample_text_data)
        assert len(entity.message_data) == 1
        assert entity.message_data[0].text == "Hello world"

    def test_message_entity_remove_content(self, sample_text_data):
        entity = MessageEntity(
            chat_uuid=str(uuid4()),
            user_uuid=str(uuid4()),
            message_data=[sample_text_data],
        )

        entity.remove_content(sample_text_data)
        assert len(entity.message_data) == 0

    def test_message_fields_enum(self):
        assert MessageFields.UUID == "uuid"
        assert MessageFields.MESSAGE_DATA == "message_data"
        assert MessageFields.CREATED_AT == "created_at"
        assert MessageFields.UPDATED_AT == "updated_at"
        assert MessageFields.CHAT_UUID == "chat_uuid"
        assert MessageFields.USER_UUID == "user_uuid"
