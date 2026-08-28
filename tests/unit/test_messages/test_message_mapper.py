import pytest
from datetime import datetime, timezone
from uuid import uuid4

from src.modules.messages.core.repositories.mappers.message_mapper import MessageMapper
from src.modules.messages.models.entities.message_entity import MessageEntity, MessageFields
from src.modules.messages.models.orm.message_orm import MessageORM
from src.general.repository.exception import NotConvertableValue


@pytest.mark.unit
class TestMessageMapper:
    def test_to_orm(self, message_mapper, sample_message_entity):
        orm = message_mapper.to_orm(sample_message_entity)
        assert isinstance(orm, MessageORM)
        assert orm.uuid == sample_message_entity.uuid
        assert len(orm.message_data) == len(sample_message_entity.message_data)
        assert orm.chat_uuid == sample_message_entity.chat_uuid
        assert orm.user_uuid == sample_message_entity.user_uuid
        assert orm.created_at == sample_message_entity.created_at
        assert orm.updated_at == sample_message_entity.updated_at

    def test_to_entity(self, message_mapper, sample_message_orm):
        entity = message_mapper.to_entity(sample_message_orm)
        assert isinstance(entity, MessageEntity)
        assert entity.uuid == sample_message_orm.uuid
        assert len(entity.message_data) == len(sample_message_orm.message_data)
        assert entity.chat_uuid == sample_message_orm.chat_uuid
        assert entity.user_uuid == sample_message_orm.user_uuid
        assert entity.created_at == sample_message_orm.created_at
        assert entity.updated_at == sample_message_orm.updated_at

    def test_to_orm_value(self, message_mapper, sample_text_data):
        field, value = message_mapper.to_orm_value(
            MessageFields.MESSAGE_DATA,
            [sample_text_data]
        )
        assert field == MessageORM.message_data
        assert len(value) == 1

    def test_to_orm_value_invalid(self, message_mapper):
        with pytest.raises(NotConvertableValue):
            message_mapper.to_orm_value(MessageFields.MESSAGE_DATA, "invalid")

    def test_to_entity_value(self, message_mapper, sample_text_data):
        field, value = message_mapper.to_entity_value(
            MessageORM.message_data,
            [sample_text_data]
        )
        assert field == MessageFields.MESSAGE_DATA
        assert len(value) == 1

    def test_to_entity_value_none(self, message_mapper):
        field, value = message_mapper.to_entity_value(
            MessageORM.message_data,
            None
        )
        assert field == MessageFields.MESSAGE_DATA
        assert value == []

    def test_to_orm_field(self, message_mapper):
        orm_field = message_mapper.to_orm_field(MessageFields.UUID)
        assert orm_field == MessageORM.uuid

        orm_field = message_mapper.to_orm_field(MessageFields.CHAT_UUID)
        assert orm_field == MessageORM.chat_uuid

    def test_to_orm_field_invalid(self, message_mapper):
        with pytest.raises(ValueError):
            message_mapper.to_orm_field("invalid_field")

    def test_to_entity_field(self, message_mapper):
        entity_field = message_mapper.to_entity_field(MessageORM.uuid)
        assert entity_field == MessageFields.UUID

        entity_field = message_mapper.to_entity_field(MessageORM.chat_uuid)
        assert entity_field == MessageFields.CHAT_UUID

    def test_field_mapping_consistency(self, message_mapper):
        for field, orm_attr in message_mapper.field_mapping.items():
            assert isinstance(field, MessageFields)
            assert hasattr(MessageORM, str(orm_attr).split('.')[-1])

    def test_get_field_name(self, message_mapper):
        name = message_mapper.get_field_name(MessageORM.uuid)
        assert name == "uuid"
        name = message_mapper.get_field_name(MessageORM.message_data)
        assert name == "message_data"
