import pytest

from src.modules.messages.types.media.models.media_message_data import (
    MediaMessageData,
    MediaMessageTypeName,
)
from src.modules.messages.types.base.base_message_data import BaseMessageData


@pytest.mark.unit
class TestMediaMessageData:
    def test_media_message_data_creation(self):
        data = MediaMessageData(
            media_url="https://example.com/media/test.jpg",
            data_type=MediaMessageTypeName,
        )
        assert data.media_url == "https://example.com/media/test.jpg"
        assert data.data_type == MediaMessageTypeName

    def test_media_message_data_defaults(self):
        data = MediaMessageData(data_type=MediaMessageTypeName)
        assert data.media_url == ""

    def test_media_message_data_inheritance(self):
        data = MediaMessageData(media_url="test.jpg", data_type=MediaMessageTypeName)
        assert isinstance(data, BaseMessageData)

    def test_media_message_type_name(self):
        assert MediaMessageTypeName == "media_message_type"
