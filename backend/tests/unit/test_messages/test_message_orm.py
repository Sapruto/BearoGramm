import pytest
from datetime import datetime
from src.modules.messages.models.orm.message_orm import MessageORM
from src.modules.messages.types.text.text_message_data import TextMessageData


@pytest.mark.unit
class TestMessageORM:
    def test_message_orm_creation(self, sample_message_orm):
        assert sample_message_orm.uuid is not None
        assert len(sample_message_orm.message_data) == 1
        assert sample_message_orm.chat_uuid is not None
        assert sample_message_orm.user_uuid is not None
        assert isinstance(sample_message_orm.created_at, datetime)
        assert sample_message_orm.updated_at is not None

    def test_message_orm_table_name(self):
        assert MessageORM.__tablename__ == "messages"

    def test_message_orm_relationships(self, sample_message_orm):
        assert hasattr(sample_message_orm, "chat")
