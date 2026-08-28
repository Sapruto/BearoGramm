import pytest
from uuid import uuid4

from src.modules.chats.core.repositories.mappers.chat_mapper import ChatMapper
from src.modules.chats.models.entities.chat_entity import ChatEntity, ChatFields
from src.modules.chats.models.orm.chat_orm import ChatORM
from src.general.repository.exception import NotConvertableValue


@pytest.mark.unit
class TestChatMapper:
    def test_to_orm_value(self, chat_mapper, sample_user_uuid, sample_companion_uuid):
        accesses = [
            {"user_uuid": sample_user_uuid},
            {"user_uuid": sample_companion_uuid}
        ]
        field, value = chat_mapper.to_orm_value(ChatFields.ACCESSES, accesses)
        assert field == ChatORM.accesses
        assert len(value) == 2

    def test_to_orm_value_invalid(self, chat_mapper):
        with pytest.raises(NotConvertableValue):
            chat_mapper.to_orm_value(ChatFields.ACCESSES, "invalid")

    def test_to_entity_value(self, chat_mapper, sample_user_uuid, sample_companion_uuid):
        accesses = [
            {"user_uuid": sample_user_uuid},
            {"user_uuid": sample_companion_uuid}
        ]
        field, value = chat_mapper.to_entity_value(ChatORM.accesses, accesses)
        assert field == ChatFields.ACCESSES
        assert len(value) == 2

    def test_to_entity_value_none(self, chat_mapper):
        field, value = chat_mapper.to_entity_value(ChatORM.accesses, None)
        assert field == ChatFields.ACCESSES
        assert value == []

    def test_to_orm_field(self, chat_mapper):
        orm_field = chat_mapper.to_orm_field(ChatFields.UUID)
        assert orm_field == ChatORM.uuid

        orm_field = chat_mapper.to_orm_field(ChatFields.ACCESSES)
        assert orm_field == ChatORM.accesses

    def test_to_orm_field_invalid(self, chat_mapper):
        with pytest.raises(ValueError):
            chat_mapper.to_orm_field("invalid_field")

    def test_to_entity_field(self, chat_mapper):
        entity_field = chat_mapper.to_entity_field(ChatORM.uuid)
        assert entity_field == ChatFields.UUID

        entity_field = chat_mapper.to_entity_field(ChatORM.accesses)
        assert entity_field == ChatFields.ACCESSES

    def test_field_mapping_consistency(self, chat_mapper):
        for field, orm_attr in chat_mapper.field_mapping.items():
            assert isinstance(field, ChatFields)
            assert hasattr(ChatORM, str(orm_attr).split('.')[-1])

    def test_get_field_name(self, chat_mapper):
        name = chat_mapper.get_field_name(ChatORM.uuid)
        assert name == "uuid"
        name = chat_mapper.get_field_name(ChatORM.accesses)
        assert name == "accesses"
