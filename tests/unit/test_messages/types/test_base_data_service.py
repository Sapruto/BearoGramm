import pytest
from unittest.mock import AsyncMock

from src.modules.messages.types.base.base_data_service import BaseDataService
from src.modules.messages.types.text.text_message_data import (
    TextMessageData,
    TextMessageTypeName,
)


class MockDataService(BaseDataService[TextMessageData]):
    async def save_data(self, raw_data):
        return TextMessageData(text=str(raw_data), data_type=TextMessageTypeName)

    async def delete_data(self, processed_data):
        return True

    async def prepare_to_save(self, data):
        return data

    async def prepare_to_use(self, data):
        return data


@pytest.mark.unit
class TestBaseDataService:
    @pytest.mark.asyncio
    async def test_save_data(self):
        service = MockDataService()
        result = await service.save_data("test")
        assert isinstance(result, TextMessageData)
        assert result.text == "test"

    @pytest.mark.asyncio
    async def test_delete_data(self):
        service = MockDataService()
        data = TextMessageData(text="test", data_type=TextMessageTypeName)
        result = await service.delete_data(data)
        assert result is True

    @pytest.mark.asyncio
    async def test_prepare_to_save(self):
        service = MockDataService()
        data = TextMessageData(text="test", data_type=TextMessageTypeName)
        result = await service.prepare_to_save(data)
        assert result == data

    @pytest.mark.asyncio
    async def test_prepare_to_use(self):
        service = MockDataService()
        data = TextMessageData(text="test", data_type=TextMessageTypeName)
        result = await service.prepare_to_use(data)
        assert result == data
