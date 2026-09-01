import pytest
from unittest.mock import AsyncMock, MagicMock

from src.modules.messages.core.services.data_processor import DataProcessor
from src.modules.messages.types.text.text_message_data import (
    TextMessageData,
    TextMessageTypeName,
)
from src.modules.messages.types.media.models.media_message_data import (
    MediaMessageData,
    MediaMessageTypeName,
)


@pytest.mark.unit
class TestDataProcessor:
    @pytest.mark.asyncio
    async def test_save_data_success(self, data_processor, mock_message_registry):
        typing_to_data = [(TextMessageTypeName, "Hello")]

        result = await data_processor.save_data(typing_to_data)

        assert result.success is True
        assert len(result.processed_data) == 1
        assert isinstance(result.processed_data[0], TextMessageData)

    @pytest.mark.asyncio
    async def test_save_data_multiple_types(
        self, data_processor, mock_message_registry
    ):
        typing_to_data = [
            (TextMessageTypeName, "Hello"),
            (MediaMessageTypeName, {"content": b"image", "filename": "test.jpg"}),
        ]

        result = await data_processor.save_data(typing_to_data)

        assert result.success is True
        assert len(result.processed_data) == 2

    @pytest.mark.asyncio
    async def test_save_data_unknown_type(self, data_processor, mock_message_registry):
        mock_message_registry.get_data_service = MagicMock(return_value=None)

        typing_to_data = [("unknown_type", "data")]

        result = await data_processor.save_data(typing_to_data)

        assert result.success is False
        assert "Unknown data type" in result.error_message

    @pytest.mark.asyncio
    async def test_save_data_exception(self, data_processor, mock_message_registry):
        mock_service = MagicMock()
        mock_service.save_data = AsyncMock(side_effect=Exception("Save error"))
        mock_message_registry.get_data_service = MagicMock(return_value=mock_service)

        typing_to_data = [(TextMessageTypeName, "Hello")]

        result = await data_processor.save_data(typing_to_data)

        assert result.success is False
        assert "Save error" in result.error_message

    @pytest.mark.asyncio
    async def test_delete_data_success(self, data_processor, mock_message_registry):
        data = [TextMessageData(text="Hello", data_type=TextMessageTypeName)]

        await data_processor.delete_data(data)

        mock_service = mock_message_registry.get_data_service()
        mock_service.delete_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_data_no_service(self, data_processor, mock_message_registry):
        mock_message_registry.get_data_service = MagicMock(return_value=None)

        data = [TextMessageData(text="Hello", data_type=TextMessageTypeName)]

        await data_processor.delete_data(data)

        mock_message_registry.get_data_service.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_data_exception(self, data_processor, mock_message_registry):
        mock_service = MagicMock()
        mock_service.delete_data = AsyncMock(side_effect=Exception("Delete error"))
        mock_message_registry.get_data_service = MagicMock(return_value=mock_service)

        data = [TextMessageData(text="Hello", data_type=TextMessageTypeName)]

        await data_processor.delete_data(data)

        mock_service.delete_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_data_success(self, data_processor, mock_message_registry):
        old_data = [TextMessageData(text="Old", data_type=TextMessageTypeName)]
        new_typing_to_data = [(TextMessageTypeName, "New")]

        mock_service = mock_message_registry.get_data_service()
        mock_service.save_data = AsyncMock(
            return_value=TextMessageData(text="New", data_type=TextMessageTypeName)
        )

        result = await data_processor.update_data(old_data, new_typing_to_data)

        assert result.success is True
        assert len(result.processed_data) == 1
        assert result.processed_data[0].text == "New"

    @pytest.mark.asyncio
    async def test_update_data_multiple_types(
        self, data_processor, mock_message_registry
    ):
        old_data = [
            TextMessageData(text="Old", data_type=TextMessageTypeName),
            MediaMessageData(media_url="old.jpg", data_type=MediaMessageTypeName),
        ]
        new_typing_to_data = [
            (TextMessageTypeName, "New"),
            (MediaMessageTypeName, {"content": b"new_image", "filename": "new.jpg"}),
        ]

        result = await data_processor.update_data(old_data, new_typing_to_data)

        assert result.success is True
        assert len(result.processed_data) == 2

    @pytest.mark.asyncio
    async def test_update_data_unknown_type(
        self, data_processor, mock_message_registry
    ):
        mock_message_registry.get_data_service = MagicMock(return_value=None)

        old_data = [TextMessageData(text="Old", data_type=TextMessageTypeName)]
        new_typing_to_data = [("unknown_type", "data")]

        result = await data_processor.update_data(old_data, new_typing_to_data)

        assert result.success is False
        assert "Unknown data type" in result.error_message

    @pytest.mark.asyncio
    async def test_update_data_rollback_on_error(
        self, data_processor, mock_message_registry
    ):
        old_data = [TextMessageData(text="Old", data_type=TextMessageTypeName)]
        new_typing_to_data = [(TextMessageTypeName, "New")]

        mock_service = MagicMock()
        mock_service.delete_data = AsyncMock(return_value=True)
        mock_service.save_data = AsyncMock(side_effect=Exception("Save error"))
        mock_message_registry.get_data_service = MagicMock(return_value=mock_service)

        result = await data_processor.update_data(old_data, new_typing_to_data)

        assert result.success is False
        assert len(result.processed_data) == 1
        assert result.processed_data[0].text == "Old"
