import pytest

from src.modules.messages.types.text.text_message_data import TextMessageData, TextMessageTypeName
from src.modules.messages.types.base.base_message_data import BaseMessageData


@pytest.mark.unit
class TestTextMessageData:
    def test_text_message_data_creation(self):
        data = TextMessageData(text="Hello", data_type=TextMessageTypeName)
        assert data.text == "Hello"
        assert data.data_type == TextMessageTypeName

    def test_text_message_data_defaults(self):
        data = TextMessageData(data_type=TextMessageTypeName)
        assert data.text == ""

    def test_text_message_data_inheritance(self):
        data = TextMessageData(text="Hello", data_type=TextMessageTypeName)
        assert isinstance(data, BaseMessageData)

    def test_text_message_data_type_name(self):
        assert TextMessageTypeName == "text_message_type"
