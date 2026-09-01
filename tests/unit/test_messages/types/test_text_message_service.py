import pytest
from unittest.mock import AsyncMock

from src.modules.messages.types.text.text_message_service import TextMessageService
from src.modules.messages.types.text.text_message_data import (
    TextMessageData,
    TextMessageTypeName,
)


@pytest.mark.unit
class TestTextMessageService:
    @pytest.mark.asyncio
    async def test_save_data_success(self, text_message_service):
        result = await text_message_service.save_data("Hello")
        assert isinstance(result, TextMessageData)
        assert result.text == "Hello"
        assert result.data_type == TextMessageTypeName

    @pytest.mark.asyncio
    async def test_save_data_empty(self, text_message_service):
        with pytest.raises(ValueError):
            await text_message_service.save_data("")

    @pytest.mark.asyncio
    async def test_save_data_too_long(self, text_message_service):
        text = "a" * 10001
        with pytest.raises(ValueError):
            await text_message_service.save_data(text)

    @pytest.mark.asyncio
    async def test_save_data_invalid_type(self, text_message_service):
        with pytest.raises(ValueError):
            await text_message_service.save_data(123)

    @pytest.mark.asyncio
    async def test_save_data_custom_max_chars(self, mock_encrypter):
        service = TextMessageService(encrypter=mock_encrypter, max_chars=5)
        result = await service.save_data("Hello")
        assert result.text == "Hello"

        with pytest.raises(ValueError):
            await service.save_data("Hello World")

    @pytest.mark.asyncio
    async def test_delete_data(self, text_message_service):
        data = TextMessageData(text="Hello", data_type=TextMessageTypeName)
        result = await text_message_service.delete_data(data)
        assert result is True

    @pytest.mark.asyncio
    async def test_prepare_to_save(self, text_message_service):
        data = TextMessageData(text="Hello", data_type=TextMessageTypeName)
        result = await text_message_service.prepare_to_save(data)
        assert result.text == "encrypted_text"

    @pytest.mark.asyncio
    async def test_prepare_to_use(self, text_message_service):
        data = TextMessageData(text="encrypted_text", data_type=TextMessageTypeName)
        result = await text_message_service.prepare_to_use(data)
        assert result.text == "decrypted_text"

    def test_get_text_message_service(self):
        from src.modules.messages.types.text.text_message_service import (
            get_text_message_service,
        )

        service = get_text_message_service()
        assert isinstance(service, TextMessageService)
