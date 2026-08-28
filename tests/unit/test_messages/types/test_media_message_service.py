import pytest
from unittest.mock import AsyncMock, MagicMock

from src.modules.messages.types.media.core.media_message_service import MediaMessageService
from src.modules.messages.types.media.models.media_message_data import MediaMessageData, MediaMessageTypeName


@pytest.mark.unit
class TestMediaMessageService:
    @pytest.mark.asyncio
    async def test_save_data_from_dict(self, media_message_service, mock_storage):
        raw_data = {
            "content": b"test image content",
            "filename": "test.jpg",
            "chat_uuid": "chat123"
        }

        result = await media_message_service.save_data(raw_data)

        assert isinstance(result, MediaMessageData)
        assert result.media_url == "https://example.com/media/test.jpg"
        assert result.data_type == MediaMessageTypeName
        mock_storage.upload_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_data_from_bytes(self, media_message_service, mock_storage):
        raw_data = {
            "content": b"test image content",
            "filename": "test.jpg"
        }
        result = await media_message_service.save_data(raw_data)
        assert isinstance(result, MediaMessageData)
        assert result.media_url == "https://example.com/media/test.jpg"
        mock_storage.upload_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_data_empty_content(self, media_message_service):
        raw_data = {"content": b"", "filename": "test.jpg"}

        with pytest.raises(ValueError):
            await media_message_service.save_data(raw_data)

    @pytest.mark.asyncio
    async def test_save_data_invalid_type(self, media_message_service):
        with pytest.raises(ValueError):
            await media_message_service.save_data("invalid")

    @pytest.mark.asyncio
    async def test_save_data_upload_failed(self, media_message_service, mock_storage):
        mock_storage.upload_file = AsyncMock(return_value=(False, "Upload error"))

        raw_data = {
            "content": b"test",
            "filename": "test.jpg"
        }

        with pytest.raises(ValueError):
            await media_message_service.save_data(raw_data)

    @pytest.mark.asyncio
    async def test_delete_data_success(self, media_message_service, mock_storage):
        data = MediaMessageData(
            media_url="https://example.com/media/test.jpg",
            data_type=MediaMessageTypeName
        )

        result = await media_message_service.delete_data(data)

        assert result is True
        mock_storage.unload_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_data_no_url(self, media_message_service):
        data = MediaMessageData(
            media_url="",
            data_type=MediaMessageTypeName
        )

        result = await media_message_service.delete_data(data)

        assert result is False
