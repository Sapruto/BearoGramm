import pytest
from pydantic import ValidationError

from src.modules.messages.types.base.base_message_data import BaseMessageData


@pytest.mark.unit
class TestBaseMessageData:
    def test_base_message_data_creation(self):
        data = BaseMessageData(data_type="test_type")
        assert data.data_type == "test_type"

    def test_base_message_data_required_fields(self):
        with pytest.raises(ValidationError):
            BaseMessageData()

    def test_base_message_data_inheritance(self, sample_text_data):
        assert isinstance(sample_text_data, BaseMessageData)
        assert sample_text_data.data_type == "text_message_type"
